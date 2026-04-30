package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/joho/godotenv"
	"github.com/parquet-go/parquet-go"
)

// SCHEMA FOR PARQUET
type Recommendation struct {
	AppID         int64   `parquet:"app_id"`
	Helpful       int64   `parquet:"helpful"`
	Funny         int64   `parquet:"funny"`
	Date          string  `parquet:"date"`
	IsRecommended bool    `parquet:"is_recommended"`
	Hours         float64 `parquet:"hours"`
	UserID        int64   `parquet:"user_id"`
	ReviewID      int64   `parquet:"review_id"`
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
		log.Fatalf("❌ ERROR CONECTING TO SUPABASE: %v", err)
	}
	defer pool.Close()
	fmt.Println("🚀 CONNECTED WITH SUPABASE.")

	filepath := "../../data/processed/recommendations_cleaned.parquet"
	fmt.Printf("\n📦 STARING INGEST FROM PARQUET: %s...\n", filepath)
	file, err := os.Open(filepath)
	if err != nil {
		log.Fatalf("❌ ERROR OPENING PARQUET: %v", err)
	}
	defer file.Close()

	reader := parquet.NewGenericReader[Recommendation](file)

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
					pgx.Identifier{"recommendations"},
					[]string{"app_id", "helpful", "funny", "date", "is_recommended", "hours", "user_id", "review_id"},
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
	recs := make([]Recommendation, 10000)
	rowsRead := 0
	limit := 2000000

	for {
		n, err := reader.Read(recs)
		if n > 0 {
			if rowsRead+n > limit {
				n = limit - rowsRead
			}
			batch := make([][]any, n)
			for i := 0; i < n; i++ {
				r := recs[i]
				batch[i] = []any{r.AppID, r.Helpful, r.Funny, r.Date, r.IsRecommended, r.Hours, r.UserID, r.ReviewID}
			}
			batches <- batch
			rowsRead += n
		}
		if err == io.EOF || rowsRead >= limit {
			break
		}
		if err != nil {
			log.Fatalf("❌ ERROR READING PARQUET: %v", err)
		}
	}

	close(batches)
	wg.Wait()
	fmt.Printf("🏁 INGESTION OF PARQUET DONE! -> %d LINES IN %v\n", totalIngested, time.Since(startTime))
}
