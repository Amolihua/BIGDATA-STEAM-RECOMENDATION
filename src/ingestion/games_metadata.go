package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

type GameMetadata struct {
	AppID       int64    `json:"app_id"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
}

func main() {
	_ = godotenv.Load("../../.env")
	dbUrl := os.Getenv("DATABASE_URL")
	if dbUrl == "" {
		log.Fatal("❌ DATABASE_URL NOT FOUND.")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbUrl)
	if err != nil {
		log.Fatalf("❌ ERROR CONNECTING TO SUPABASE: %v", err)
	}
	defer pool.Close()

	filepath := "../../data/processed/games_metadata_cleaned.json"
	fmt.Printf("🚀 STARTING CONCURRENT INGESTION OF METADATA: %s\n", filepath)

	file, err := os.Open(filepath)
	if err != nil {
		log.Fatalf("❌ ERROR OPENING %s: %v", filepath, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	buf := make([]byte, 0, 64*1024)
	scanner.Buffer(buf, 1024*1024)

	batches := make(chan [][]any, 50)
	var wg sync.WaitGroup
	var mu sync.Mutex
	totalIngested := 0
	numWorkers := 8

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for batch := range batches {
				_, err := pool.CopyFrom(
					ctx,
					pgx.Identifier{"games_metadata"},
					[]string{"app_id", "description", "tags"},
					pgx.CopyFromRows(batch),
				)
				if err != nil {
					log.Printf("❌ WORKER %d ERROR: %v\n", workerID, err)
					continue
				}
				mu.Lock()
				totalIngested += len(batch)
				mu.Unlock()
			}
		}(i)
	}

	startTime := time.Now()
	var currentBatch [][]any
	batchSize := 2000

	for scanner.Scan() {
		var md GameMetadata
		if err := json.Unmarshal(scanner.Bytes(), &md); err != nil {
			continue
		}
		tagsJson, _ := json.Marshal(md.Tags)

		currentBatch = append(currentBatch, []any{md.AppID, md.Description, string(tagsJson)})

		if len(currentBatch) == batchSize {
			batches <- currentBatch
			currentBatch = make([][]any, 0, batchSize)
		}
	}

	if len(currentBatch) > 0 {
		batches <- currentBatch
	}

	close(batches)
	wg.Wait()
	fmt.Printf("🏁 INGESTION OF METADATA DONE! -> %d LINES IN %v\n", totalIngested, time.Since(startTime))
}
