package main

import (
	"fmt"
	"math/rand"
	"time"
)

// Section 1: Constants for Grid and Agents

const (
	width             = 51 // Adjusted for 40 spaces + Moses + 10 for followers
	height            = 20 // Adjustable as needed
	followMosesChance = 70
	turnsForThirst    = 2
	turnsForVillage   = 5
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
	g[startRow+2][10].Type = "M" // Moses is placed 10 columns away from 0th column
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
	rand.Seed(time.Now().UnixNano())

	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			cell := &g[y][x]
			if cell.Type == "I" {
				for move := 0; move < 2; move++ { // Allow two moves per turn
					direction := rand.Intn(100)
					moveTowardsMoses := direction < followMosesChance
					var newY, newX int

					if moveTowardsMoses {
						// Move in the same direction as Moses
						newX = x + 1
						newY = y
					} else {
						// Move in a random direction
						newY = y + rand.Intn(3) - 1 // -1, 0, or 1
						newX = x + rand.Intn(3) - 1 // -1, 0, or 1
					}

					// Check boundaries and occupancy
					if newY >= 0 && newY < height && newX >= 0 && newX < width && g[newY][newX].Type == " " {
						// Perform the move
						g[newY][newX] = *cell
						cell.Type = " "
						cell.Index = 0
						// Update the current position for the next move
						x = newX
						y = newY
					}
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

// ApplyRules applies the rules for thirst and village formation
func (g *Grid) ApplyRules() {
	// Apply thirst and village formation rules
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			cell := &g[y][x]
			if cell.Type == "I" {
				distance := g.DistanceFromMoses(y, x)
				adjacentFollowers := g.CheckAdjacentFollowers(y, x)

				// Update distance counter
				if distance >= 10 {
					cell.FollowerInfo.DistanceCounter++
				} else {
					cell.FollowerInfo.DistanceCounter = 0
				}

				// Check for followers dying of thirst
				if cell.FollowerInfo.DistanceCounter >= turnsForThirst && adjacentFollowers <= 2 {
					cell.Type = "D" // Follower dies of thirst
				}

				// Check for village formation
				if cell.FollowerInfo.DistanceCounter >= turnsForVillage && adjacentFollowers >= 3 {
					// Make sure all adjacent followers are also more than 10 spaces away for 2 turns
					allQualifyForVillage := true
					for dy := -1; dy <= 1; dy++ {
						for dx := -1; dx <= 1; dx++ {
							if !(dy == 0 && dx == 0) && y+dy >= 0 && y+dy < height && x+dx >= 0 && x+dx < width {
								adjCell := &g[y+dy][x+dx]
								if adjCell.Type == "I" && adjCell.FollowerInfo.DistanceCounter < 2 {
									allQualifyForVillage = false
								}
							}
						}
					}

					if allQualifyForVillage {
						cell.Type = "V" // Followers form a village
					}
				}
			}
		}
	}
}

// CheckAdjacentFollowers counts the adjacent followers
func (g *Grid) CheckAdjacentFollowers(y, x int) int {
	count := 0
	for dy := -1; dy <= 1; dy++ {
		for dx := -1; dx <= 1; dx++ {
			if !(dy == 0 && dx == 0) && y+dy >= 0 && y+dy < height && x+dx >= 0 && x+dx < width {
				if g[y+dy][x+dx].Type == "I" {
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
	fmt.Println("       *                ")
	fmt.Println("      ***          __   ")
	fmt.Println("     *****       _|==|_ ")
	fmt.Println("    *******       ('')_/")
	fmt.Println("   *********  >--(`^^') ")
	fmt.Println("  ***********   (`^'^'`)")
	fmt.Println("     |||||      `======'")
	fmt.Println(" ")
	fmt.Println(" ")
	// Print the Merry Christmas message
	fmt.Println("Merry Christmas to Jae, Manfred, and quite literally the rest of the company from Michael, the whole Gnoland team, and everyone else working on quant tasks & tokenomics with us.")
	fmt.Println("Genuinely, thank you everyone for everything you do.")
}
