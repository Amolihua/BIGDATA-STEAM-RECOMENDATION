package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
)

func main() {
	_ = godotenv.Load("../../.env")
	dbUrl := os.Getenv("DATABASE_URL")
	if dbUrl == "" {
		log.Fatal("❌ DATABASE_URL no encontrada en el entorno.")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbUrl)
	if err != nil {
		log.Fatalf("❌ Error conectando a Supabase: %v", err)
	}
	defer pool.Close()

	filepath := "../../data/processed/users_cleaned.csv"
	fmt.Printf("🚀 Iniciando ingesta CONCURRENTE de USERS: %s\n", filepath)

	file, err := os.Open(filepath)
	if err != nil {
		log.Fatalf("❌ Error abriendo %s: %v", filepath, err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, _ = reader.Read()

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
					pgx.Identifier{"users"},
					[]string{"user_id", "products", "reviews"},
					pgx.CopyFromRows(batch),
				)
				if err != nil {
					log.Printf("❌ Worker %d error: %v\n", workerID, err)
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
	batchSize := 5000 // Users es más simple, batches más grandes

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			continue
		}
		row := make([]any, len(record))
		for i, v := range record {
			row[i] = v
		}
		currentBatch = append(currentBatch, row)

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
	fmt.Printf("🏁 INGESTA USERS COMPLETADA: %d filas en %v\n", totalIngested, time.Since(startTime))
}
