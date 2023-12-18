package main

import (
	"fmt"
	"math/rand"
	"time"
)

// Section 1: Constants for Grid and Agents

const (
	width  = 51 // Adjusted for 40 spaces + Moses + 10 for followers
	height = 25 // Adjustable as needed
)

// FollowerState holds additional state information for a follower
type FollowerState struct {
	DistanceCounter int // Counts turns more than 10 spaces away from Moses
}

// Cell represents a grid cell with a type and an index for followers
type Cell struct {
	Type         string // "M" for Moses, "I" for followers, "D" for deceased, "V" for village, " " for empty
	Index        int    // Index for followers
	FollowerInfo FollowerState
}

// Grid represents the simulation grid
type Grid [height][width]Cell

// Initialize the grid with Moses and followers
func (g *Grid) Initialize() {
	followerCount := 0
	// Calculate the start row for followers to be centered vertically behind Moses
	startRow := height/2 - 2 // This is the row for "I1"

	for i := 0; i < 5; i++ {
		for j := 0; j < 10; j++ {
			followerCount++
			g[startRow+i][j].Type = "I"
			g[startRow+i][j].Index = followerCount
		}
	}
	// Place Moses ahead of the followers, on the same row as the middle follower
	g[startRow+2][10].Type = "M" // Moses is placed 10 columns away from the 0th column
}

// Display prints the current state of the grid
func (g *Grid) Display(year int) {
	egyptLabel := "EGYPT"

	// Calculate the row index for "Y" to be in line with Moses' path
	yRowIndex := height/2 - 1

	// Print the current year above the grid
	fmt.Printf("Year %d:\n", year)

	// Print the grid
	for i := 0; i < height; i++ {
		// Print the EGYPT label vertically on the left side
		if i >= yRowIndex-1 && i <= yRowIndex+3 {
			fmt.Printf("%c ", egyptLabel[i-yRowIndex+1])
		} else {
			fmt.Print("  ") // Add spacing to align the grid properly
		}

		// Print the grid cells
		for j := 0; j < width; j++ {
			cell := g[i][j]
			if cell.Type == "I" && cell.Index > 0 {
				fmt.Printf("%s%d ", cell.Type, cell.Index) // Print followers with index
			} else {
				fmt.Printf("%s  ", cell.Type) // Print empty cells or Moses
			}
		}

		// Print a newline at the end of each grid row
		fmt.Println()
	}
}

// Section 2: Movement and Grid Distances

// MoveMoses advances Moses one step to the right
func (g *Grid) MoveMoses() {
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if g[y][x].Type == "M" {
				// Check if Moses is at the second to last column, stop him from moving further
				if x < width-len("ISRAEL")-2 {
					g[y][x+1].Type = "M"
					g[y][x].Type = " "
				}
				return
			}
		}
	}
}

// MoveFollowers handles the movement of each follower
func (g *Grid) MoveFollowers() {
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			if g[y][x].Type == "I" {
				newY, newX := y, x
				if rand.Intn(2) == 0 { // 50% chance to move in the same direction as Moses
					newX++
				} else {
					// Random movement including diagonal
					newY += rand.Intn(3) - 1 // -1, 0, or 1
					newX += rand.Intn(3) - 1 // -1, 0, or 1
				}

				// Check boundaries and occupancy
				if newY >= 0 && newY < height && newX >= 0 && newX < width && g[newY][newX].Type == " " {
					g[newY][newX] = g[y][x]
					g[y][x].Type = " "
					g[y][x].Index = 0
				}
			}
		}
	}
}

// IsSpaceFree checks if a given grid cell is free (not occupied)
func (g *Grid) IsSpaceFree(y, x int) bool {
	return y >= 0 && y < height && x >= 0 && x < width && g[y][x].Type == " "
}

// DistanceFromMoses calculates the distance of a cell from Moses
func (g *Grid) DistanceFromMoses(y, x int) int {
	// Find Moses' position
	mosesX := -1
	for i := 0; i < width; i++ {
		if g[height/2][i].Type == "M" {
			mosesX = i
			break
		}
	}

	if mosesX == -1 {
		return -1 // Moses not found
	}

	return abs(x - mosesX)
}

// abs returns the absolute value of an integer
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// Section 3: Apply Rules and Logic

// Part 3 continues from the previous code

// ApplyRules applies the rules for thirst and village formation
func (g *Grid) ApplyRules() {
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			cell := &g[y][x]
			if cell.Type == "I" {
				distance := g.DistanceFromMoses(y, x)

				// Update distance counter
				if distance > 10 {
					cell.FollowerInfo.DistanceCounter++
				} else {
					cell.FollowerInfo.DistanceCounter = 0
				}

				// Check for thirst condition
				if cell.FollowerInfo.DistanceCounter >= 2 {
					cell.Type = "D"
				}

				// Check for village formation
				if cell.FollowerInfo.DistanceCounter >= 10 && g.CheckAdjacentFollowers(y, x) >= 3 {
					cell.Type = "V"
				}
			}
		}
	}
}

// CheckAdjacentFollowers counts adjacent followers
func (g *Grid) CheckAdjacentFollowers(y, x int) int {
	count := 0
	for i := -1; i <= 1; i++ {
		for j := -1; j <= 1; j++ {
			if !(i == 0 && j == 0) && y+i >= 0 && y+i < height && x+j >= 0 && x+j < width {
				if g[y+i][x+j].Type == "I" {
					count++
				}
			}
		}
	}
	return count
}

// NextTurn updates the grid to its next state
func (g *Grid) NextTurn() {
	g.MoveMoses()
	g.MoveFollowers()
	g.ApplyRules()
}

// main is the entry point of the program
func main() {
	rand.Seed(time.Now().UnixNano()) // Initialize the random seed once

	var grid Grid
	grid.Initialize()
	grid.Display(0) // Display initial state of the grid with year 0

	for turn := 1; turn <= 40; turn++ {
		time.Sleep(750 * time.Millisecond) // Pause between turns for visibility
		grid.MoveMoses()                   // Move Moses one step to the right
		grid.MoveFollowers()               // Move followers according to the rules
		grid.ApplyRules()                  // Apply rules for thirst and village formation
		grid.Display(turn)                 // Display state of the grid with the current year
	}
}
