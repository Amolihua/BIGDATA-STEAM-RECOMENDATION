package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"sync"
	"time"

	"github.com/parquet-go/parquet-go"
)

// Review define el esquema del Parquet.
type Review struct {
	AppID           int64  `parquet:"app_id"`
	SteamID         string `parquet:"steam_id"`
	PlaytimeForever int64  `parquet:"playtime_forever"`
	VotedUp         bool   `parquet:"voted_up"`
	ReviewText      string `parquet:"review_text"`
}

// SteamAPIResponse estructura el JSON de respuesta.
type SteamAPIResponse struct {
	Success int    `json:"success"`
	Cursor  string `json:"cursor"`
	Reviews []struct {
		Author struct {
			SteamID         string `json:"steamid"`
			PlaytimeForever int64  `json:"playtime_forever"`
		} `json:"author"`
		VotedUp bool   `json:"voted_up"`
		Review  string `json:"review"`
	} `json:"reviews"`
}

func main() {

	appIDs, err := cargarAppIDs("../../data/interim/target_app_ids.json")
	if err != nil {
		log.Fatalf("❌ Error cargando los App IDs: %v\nPor favor ejecuta la extracción del JSON en tu notebook primero.", err)
	}
	fmt.Printf("🎯 Iniciando procesamiento de %d juegos en paralelo...\n", len(appIDs))

	outputFile, err := os.Create("../../data/processed/steam_interactions_v1.parquet")
	if err != nil {
		log.Fatalf("❌ Error creando el archivo parquet: %v", err)
	}
	defer outputFile.Close()

	writer := parquet.NewGenericWriter[Review](outputFile)

	tasksChan := make(chan int, len(appIDs))
	resultsChan := make(chan []Review, 50)

	for _, id := range appIDs {
		tasksChan <- id
	}
	close(tasksChan)

	var wg sync.WaitGroup
	var writerWg sync.WaitGroup

	writerWg.Add(1)
	go func() {
		defer writerWg.Done()
		totalReviews := 0
		for batch := range resultsChan {
			if len(batch) > 0 {
				_, err := writer.Write(batch)
				if err != nil {
					log.Printf("⚠️ Error escribiendo al parquet: %v", err)
				}
				totalReviews += len(batch)
			}
		}
		fmt.Printf("✅ Escritura finalizada. Total de reviews almacenadas: %d\n", totalReviews)
	}()

	// Core i7-10700 con 16 hilos lógicos. Usando 12 workers.
	numWorkers := 12
	httpClient := &http.Client{Timeout: 10 * time.Second}

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()

			for appID := range tasksChan {
				obtenerResenas(httpClient, appID, resultsChan)
			}
		}(i)
	}

	wg.Wait()
	close(resultsChan)
	writerWg.Wait()

	err = writer.Close()
	if err != nil {
		log.Fatalf("Error cerrando writer parquet: %v", err)
	}

	fmt.Println("PROCESAMIENTO COMPLETADO")
}

func obtenerResenas(client *http.Client, appID int, resultsChan chan<- []Review) {
	cursor := "*"
	recolectadas := 0
	maxPorJuego := 1000

	for recolectadas < maxPorJuego {
		encodedCursor := url.QueryEscape(cursor)
		apiURL := fmt.Sprintf("https://store.steampowered.com/appreviews/%d?json=1&filter=recent&language=english&cursor=%s&num_per_page=100", appID, encodedCursor)

		resp, err := client.Get(apiURL)
		if err != nil {
			log.Printf("⚠️ Error en req appID %d: %v", appID, err)
			break
		}

		if resp.StatusCode == 429 {
			log.Printf("⚠️ Rate limit HTTP 429 en appID %d. Pausando 10s...", appID)
			resp.Body.Close()
			time.Sleep(10 * time.Second)
			continue
		}

		if resp.StatusCode != 200 {
			resp.Body.Close()
			break
		}

		var steamResp SteamAPIResponse
		err = json.NewDecoder(resp.Body).Decode(&steamResp)
		resp.Body.Close()

		if err != nil || len(steamResp.Reviews) == 0 {
			break
		}

		var block []Review
		for _, rw := range steamResp.Reviews {
			block = append(block, Review{
				AppID:           int64(appID),
				SteamID:         rw.Author.SteamID,
				PlaytimeForever: rw.Author.PlaytimeForever,
				VotedUp:         rw.VotedUp,
				ReviewText:      rw.Review,
			})
		}

		recolectadas += len(block)
		resultsChan <- block

		if steamResp.Cursor == cursor {
			break
		}
		cursor = steamResp.Cursor

		time.Sleep(200 * time.Millisecond)
	}
}

func cargarAppIDs(ruta string) ([]int, error) {
	file, err := os.Open(ruta)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var ids []int
	rawBytes, _ := io.ReadAll(file)
	err = json.Unmarshal(rawBytes, &ids)
	return ids, err
}
