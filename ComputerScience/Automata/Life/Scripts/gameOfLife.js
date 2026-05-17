/*-----------------------------------------------------------------------------
|
| NAME
|
|     gameOfLife.js
|
| DESCRIPTION
|
|     A JavaScript version of the cellular automata Game of Life by
|     Cambridge University mathematician John Horton Conway.
|
| METHOD
|
|     Life is played on a two dimensional game board which is partitioned
|     into cells.  Cells may be occupied with counters.
|
|     By default, we use these three (J.H. Conway) rules:
|
|     1.  BIRTH.  Each empty cell adjacent to exactly 3 neighbors will have a
|         birth in the next generation.  Otherwise, the cell remains empty.
|
|     2.  DEATH.  Each occupied cell with exactly 0 or 1 neighbors dies of
|         isolation and loneliness.  Each occupied cell with 4 or more
|         neighbors dies of overpopulation.
|
|     3.  SURVIVAL.  Each occupied cell with exactly 2 or 3 neighbors survives
|         to the next generation.
|
|     All births and deaths occur simultaneously.  Applying all rules to an
|     entire board creates a new generation.  Ultimately, the society dies
|     out, reaches some steady state (constant or oscillating) or the user
|     gets bored.
|
|     The ideal game board is infinite.  For this program, we wrap around
|     at the boundaries of the board so that it is topologically a torus.
|
|     See Mathematical Games, SCIENTIFIC AMERICAN, Vol. 223, No. 4,
|     October 1970, pgs. 120-123 for a description of the game.
|
| LEGAL
|
|     JavaScript Game Of Life Version 3.4 -
|     A JavaScript version of the cellular automata Game of Life by J. H. Conway.
|     Copyright (C) 2010-2026 by Sean Erik O'Connor.  All Rights Reserved.
|
|     This program is free software: you can redistribute it and/or modify
|     it under the terms of the GNU General Public License as published by
|     the Free Software Foundation, either version 3 of the License, or
|     (at your option) any later version.
|
|     This program is distributed in the hope that it will be useful,
|     but WITHOUT ANY WARRANTY; without even the implied warranty of
|     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
|     GNU General Public License for more details.
|
|     You should have received a copy of the GNU General Public License
|     along with this program.  If not, see <http://www.gnu.org/licenses/>.
|
|     The author's address is seanerikoconnor!AT!gmail!DOT!com
|     with !DOT! replaced by . and the !AT! replaced by @
|
-----------------------------------------------------------------------------*/

// I'm going to use JavaScript's prototypal inheritance model and NOT the class/instance model which
// was crudely slapped on top to make the language seem OO.

// I ran through JSLint https://www.jslint.com/ to check for errors. Be aware that some messages
// such as "unexpected this' or 'unexpected let' are not errors, but just Doug Crawford's preferences.
// On Ubuntu/Linux,
//     sudo apt install curl
//     sudo apt install nodejs
//     curl -L https://www.jslint.com/jslint.mjs > jslint.mjs
//     node jslint.mjs Scripts/gameOfLife.js

//======================================= Game of Life Object ==========================================================

// Create basic game of life object with default settings which has a prototype chain.
const gameOfLifeBase =
{
    DebugPrintOptions :
    {
        GameBoard : 0,
        Neighbors : 1,
        States    : 2
    },

    // Maximum values for game board dimensions.
    GameSettings :
    {
        GameBoardNumCols   : 100,
        GameBoardNumRows   : 100,
        MaxFileLineLength  : 80,
        MaxNumCommentLines : 22,
        MaximumAge         : 10000,
        OldAge             : 50,
        UpdateIntervalMs   : 50
    },

    getAccessToDOMElements: function()
    {
        // Get access to the document's canvas, control buttons, output windows, file select buttons, etc.
        this.GameOfLifeCanvas    = document.getElementById( "GameOfLifeCanvas" ) ;
        this.GameOfLifeState     = document.getElementById( "GameOfLifeState" ) ;
        this.GameOfLifeCellState = document.getElementById( "GameOfLifeCellState" ) ;
        this.GameOfLifeDebug     = document.getElementById( "GameOfLifeDebug" ) ;
        this.GameOfLifeLoadFile  = document.getElementById( "GameOfLifeLoadFile" ) ;
        this.GameOfLifeClipboard = document.getElementById( "GameOfLifeClipboard" ) ;
        this.GameOfLifePatterns  = document.getElementById( "GameOfLifePatterns" ) ;

        // We have a group of boxes and radio buttons sharing the same name so we can fetch all of 
        // their values as an array.  We can't use id's since they are unique to a single element.
        this.GameOfLifeSurvivalRules = document.getElementsByName( "GameOfLifeSurvivalRules" ) ;
        this.GameOfLifeBirthRules    = document.getElementsByName( "GameOfLifeBirthRules" ) ;
    },

    timer : undefined,

    addEventListeners: function()
    {
        // Register the callback function which is called when mouse cursor is clicked anywhere on 
        // the canvas.
        this.GameOfLifeCanvas.addEventListener( "click", make_onCanvasMouseClick( this ), false ) ;

        // Register the callback function which is called when the mouse moves in the canvas.
        this.GameOfLifeCanvas.addEventListener( "mousemove", make_onCanvasMouseMove( this ), false ) ;

        // Register the callback function which is called when the LoadLifeFileButton button is 
        // clicked.  The function argument is an event which is the list of files selected.
        this.GameOfLifeLoadFile.addEventListener( "change", make_GameOfLifeLoadFile( this ), false ) ;

        // Register the callback function for the GameOfLifePatterns form selector which is called when
        // a pattern is selected from the list.  The event contains the pattern string.
        this.GameOfLifePatterns.addEventListener( "change", make_loadSampleLifePattern( this ));
    }
}

// Create a single global object for the Game of Life from the default object and link it into the prototype chain.
let gameOfLife = Object.create( gameOfLifeBase ) ;

//================================================ Game Board Object ========================================================================

// Create basic game of life object with default settings which has a prototype chain.
const GameBoardBase =
{
    GameOfLifeCanvas : undefined,
    widthPixels :  0,
    heightPixels : 0,
    graphicsContext  : undefined,
}

// Create a single global object for the Game Board from the default object and link it into the prototype chain.
let gameBoard = Object.create( GameBoardBase )

//===================================================== Game Board Objects ===========================================================

//  Define some "enum" types as class let, e.g. if (x === Occupancy.Empty) ...
const Occupancy =
{
    Indeterminate : -1, // No occupancy state at the beginning.
    Empty         :  0, // Cell is empty.
    Occupied      :  1  // Cell has a counter in it.
} ;

const State =
{
    Indeterminate : -1, // No state at the beginning.
    Survival      :  0, // Survives;  no change from last time.
    Birth         :  1, // Empty cell has a birth.
    Death         :  2  // Occupied cell dies.

} ;

//================================================ Game of Life Member Functions =====================================================

// Attach the game board to the Game of Life App
gameOfLife.gameBoard = gameBoard

// Initialize game of life app.
gameOfLife.init = function()
{
    this.getAccessToDOMElements() ;
    this.initGameBoard() ;
    this.preloadPatterns() ;
    this.addEventListeners() ;
}

gameOfLife.initGameBoard = function()
{
    // Create a new game board which is the size of the canvas and pass it the canvas graphics context.
    this.gameBoard.init( this.GameSettings, make_debugPrint( this ), this.DebugPrintOptions, this.GameOfLifeCanvas, this.GameOfLifeState )

    // Draw the life grid lines.
    this.gameBoard.drawLifeGrid() ;

    // Clear the game state.
    this.gameBoard.clearGameState() ;
}

gameOfLife.preloadPatterns = function()
{
    // Preload a few examples of life into this.listOfSampleLifePatterns.
    // Then load a glider gun.
    this.preloadLifePatterns() ;
    this.readLifeFile( this.sampleLifePatterns[ "glidergun" ] ) ;

    // Work around a Firefox bug which doesn't select the default in the drop down form
    // when refreshing the page:
    //    https://stackoverflow.com/questions/4831848/firefox-ignores-option-selected-selected
    window.onload = function() { document.forms[ "GameOfLifePatternsForm" ].reset() } ;

    // Write game to clipboard.
    this.writeGameToClipboard() ;

    // Update all counters.
    this.gameBoard.updateView() ;

    // Update the rules.
    this.updateRulesView() ;
}

// Advance the game one generation.
gameOfLife.cycleGame = function ()
{
    // Update the game board.
    this.gameBoard.updateGameBoard() ;

    // Repaint the canvas, but only for counters which have changed.
    this.gameBoard.updateView() ;
}

// Callback function to clear the game state.
gameOfLife.clearGame = function ()
{
    this.gameBoard.clearGameState() ;
    this.gameBoard.updateView() ;
}

// Callback function to change the life rules.  flag = true for survivals, false for births.
gameOfLife.changeRules = function( flag )
{
    let rulesElement = undefined ;

    // Pick the rule type.
    if (flag)
        rulesElement = this.GameOfLifeSurvivalRules ;
    else
        rulesElement = this.GameOfLifeBirthRules ;

    let numNeighbors = [] ;
    let numRules = 0 ;

    // Iterate over the whole group of checkboxes for number of neighbors for either survivals or births.
    //
    //                                +-+        +-+              +-+
    //     Neighbors to survive     1 |X|      2 |X|  . . .     8 | |     rulesElement = HTML element which
    //                                +-+        +-+              +-+     contains this row of 8 boxes.
    //
    //                                +-+        +-+              +-+
    //     Neighbors for birth      1 | |      2 | |  . . .     8 | | 
    //                                +-+        +-+              +-+
    //
    //     boxNum                      0          1                7
    //   
    //   In this example, a cell can have either 1 or 2 neighbors to survive, so there are two rules.
    //   numRules           2
    //   numNeighbors       [1, 2]
    numBoxes = rulesElement.length ;
    for (let boxNum = 0 ;  boxNum < numBoxes ;  ++boxNum)
    {
        if (rulesElement[ boxNum ].checked)
        {
            numNeighbors[ numRules++ ] = boxNum + 1 ;
        }
    }

    let rules = 
    {
        numNeighbors : numNeighbors,
        numRules     : numRules
    }

    /* Aside:
       How would we have created the "rules" object using the phony class-based syntax which
       pretends JavaScript has classes which instantiate objects using constructors?

       This ignores that underneath, JavaScript has NO classes, NO inheritance from parent class to child class, and NO object instantiation from a class.
       There are only objects dynamically connected by prototype chains.  Totally different language design concepts:  no wonder class/object people have problems.

        //   Create a base rules object for the number of neighbors required 
        //   for either survivals or births.  For example,
        //       let survival_rules = new Rules( 2, [2, 3])
        //       let birth_rules    = new Rules( 1, [3])
        //
        //   This is the constructor function (by custom, the name starts with a capital letter).
        //   Is to be called using operator "new" to create the new rules object.

        function Rules( numRules, neighborCounts )
        {
            // Allow up to 9 rules since we can have 0-8 neighbors.
            this.numNeighbors = new Array( 9 ) ;

            // Fill all rules, leaving other undefined.
            for (let i = 0 ;  i < neighborCounts.length ;  ++i)
                this.numNeighbors[ i ] = neighborCounts[ i ] ;

            this.numRules = numRules ;
        } ;

        // Create a new "rules" object using the new constructor.
        let rules = new Rules( numRules, numNeighbors ) ;
    */

    if (flag)
        this.gameBoard.rules.survival = rules ;
    else
        this.gameBoard.rules.birth = rules ;

    this.gameBoard.updateView() ;
}

// Update the rules view.
gameOfLife.updateRulesView = function()
{
    // Uncheck all the boxes first.
    for (let boxNum = 0 ;  boxNum < this.GameOfLifeSurvivalRules.length ;  ++boxNum)
        this.GameOfLifeSurvivalRules[ boxNum ].checked = false ;

    // Go through all the rules, checking boxes with number of neighbors.
    for (let i = 0 ; i < this.gameBoard.rules.survival.numRules ;  ++i)
        this.GameOfLifeSurvivalRules[ this.gameBoard.rules.survival.numNeighbors[ i ] - 1].checked = true ;

    // Uncheck all the boxes first.
    for (let boxNum = 0 ;  boxNum < this.GameOfLifeBirthRules.length ;  ++boxNum)
        this.GameOfLifeBirthRules[ boxNum ].checked = false ;

    // Go through all the rules, checking boxes with number of neighbors.
    for (let i = 0 ; i < this.gameBoard.rules.birth.numRules ;  ++i)
        this.GameOfLifeBirthRules[ this.gameBoard.rules.birth.numNeighbors[ i ] - 1].checked = true ;
}

// Save the game to the clipboard.
gameOfLife.writeGameToClipboard = function()
{
    this.GameOfLifeClipboard.value = this.writeLifeFile( this.gameBoard ) ;
}

// Read a game from the clipboard.
gameOfLife.readGameFromClipboard = function()
{
    // Clear out the game board, load the file from the clipboard area, update the gameboard view, status and rules.
    this.gameBoard.clearGameState() ;
    this.readLifeFile( this.GameOfLifeClipboard.value ) ;
    this.gameBoard.updateView() ;
    this.updateRulesView() ;
}

// Enable or disable the timer for running the game.
gameOfLife.runStopGame = function()
{
    if (this.timer === undefined)
        this.timer = setInterval( make_cycleGame( this ), this.GameSettings.UpdateIntervalMs ) ;
    else
    {
        clearInterval( this.timer ) ;
        this.timer = undefined ;
    }
}

// Callback function to single step the game.
gameOfLife.singleStepGame = function()
{
    // Stop the game from running by disabling th timer.
    if (this.timer !== undefined)
    {
        clearInterval( this.timer ) ;
        this.timer = undefined ;
    }

    this.cycleGame() ;
}

// Debug print the game board counters.
gameOfLife.printGameBoard = function()
{
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    // Display the game board counters.
    let text = "Game Board\n" ;
    for (let row = 0 ;  row < numRows ;  ++row)
    {
        // Up to 5 digit number with padding.  Concatenate blanks to the front of the number, then take 5 chars back from the end.
        text += String( "     " + row ).slice( -5 ) ;
        text += ":" ;
        for (let col = 0 ;  col < numCols ;  ++col)
        {
            let cell = this.gameBoard.cell[ row ][ col ] ;
            if (cell.occupied === Occupancy.Occupied)
                text += "O" ;
            else
                text += "." ;
        }
        text += "\n" ;
    }

    return text ;
}

// Debug print the game board neighbor counts.
gameOfLife.printNeighborCounts = function()
{
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    // Display the neighbor counts.
    let text = "Neighbor counts\n" ;
    for (let row = 0 ;  row < numRows ;  ++row)
    {
        // Up to 5 digit number with padding.  Concatenate blanks to the front of the number, then take 5 chars back from the end.
        text += String( "     " + row ).slice( -5 ) ;
        text += ":" ;
        for (let col = 0 ;  col < numCols ;  ++col)
        {
            let cell = this.gameBoard.cell[ row ][ col ] ;
            let num  = cell.numberOfNeighbors ;
            text += (num === 0 ? "." : num) ;
        }
        text += "\n" ;
    }
    return text ;
}

// Debug print the game board counter states.
gameOfLife.printCounterState = function()
{
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    // Display the counter states.
    let text = "Counter state\n" ;
    for (let row = 0 ;  row < numRows ;  ++row)
    {
        // Up to 5 digit number with padding.  Concatenate blanks to the front of the number, then take 5 chars back from the end.
        text += String( "     " + row ).slice( -5 ) ;
        text += ":" ;
        for (let col = 0 ;  col < numCols ;  ++col)
        {
            let cell = this.gameBoard.cell[ row ][ col ] ;
            if (cell.state === State.Birth)
                text += "B" ;
            else if (cell.state === State.Survival)
                text += "s" ;
            else if (cell.state === State.Death)
                text += "d" ;
            else
                text += "." ;
        }
        text += "\n" ;
    }

    return text ;
}

// A small collection of life patterns.
gameOfLife.preloadLifePatterns = function()
{
    // Just load these sample life patterns, indexed by name into an associative array.

    this.sampleLifePatterns =
    {
        glidergun :

        "#Life 1.05\n" +
        "#D p30 glider gun (the Original)\n" +
        "#D This is made of two of a pattern\n" +
        "#D known as the \"queen bee\", which\n" +
        "#D sometimes occurs naturally,\n" +
        "#D whose debris can be deleted on\n" +
        "#D the sides by blocks or eaters.\n" +
        "#D But a collision in the center\n" +
        "#D can, as seen here, miraculously \n" +
        "#D form a glider. Just one of these\n" +
        "#D moving back and forth is called\n" +
        "#D piston (see the p30 in OSCSPN2).\n" +
        "#D  I added an eater at the bottom right.\n" +
        "#N\n" +
        "#P 4 -5\n" +
        "....*\n" +
        ".****\n" +
        "****\n" +
        "*..*\n" +
        "****\n" +
        ".****\n" +
        "....*\n" +
        "#P 13 -4\n" +
        "*\n" +
        "*\n" +
        "#P -6 -3\n" +
        "..*\n" +
        ".*.*\n" +
        "*...**\n" +
        "*...**\n" +
        "*...**\n" +
        ".*.*\n" +
        "..*\n" +
        "#P 17 -2\n" +
        "**\n" +
        "**\n" +
        "#P -17 0\n" +
        "**\n" +
        "**\n" +
        "#P 42 40\n" +
        "**\n" +
        "*.*\n" +
        "..*\n" +
        "..**\n" +
        "",

        replicator :

        "#Life 1.05\n" +
        "#D In February 1994, Nathan Thompson reported several interesting objects\n" +
        "#D that he found in a cellular automaton closely related to Conway's Life.\n" +
        "#D The reason that HighLife has been investigated so much is because of the\n" +
        "#D object known as the 'replicator'.  This amazing object starts with only\n" +
        "#D six live cells as shown in figure 2.  See 'HighLife - An Interesting\n" +
        "#D Variant of Life (part 1/3)', by David I. Bell, dbell@canb.auug.org.au,\n" +
        "" +
        "#D 7 May 1994.\n" +
        "" +
        "#R 23/36\n" +
        "" +
        "#P -2 -2\n" +
        "" +
        ".***\n" +
        "" +
        "*...\n" +
        "" +
        "*...\n" +
        "" +
        "*...\n" +
        "" +
        "",
        
        crab :

        "#Life 1.05\n" +
        "" +
        "#D Name: Crab\n" +
        "" +
        "#D Author: Jason Summers\n" +
        "" +
        "#D The smallest known diagonal spaceship other than the glider. It was discovere\n" +
        "" +
        "#D d in September 2000.\n" +
        "" +
        "#D www.conwaylife.com/wiki/index.php?title=Crab\n" +
        "#N\n" +
        "#P -6 -6\n" +
        "........**\n" +
        ".......**\n" +
        ".........*\n" +
        "...........**\n" +
        "..........*\n" +
        ".\n" +
        ".........*..*\n" +
        ".**.....**\n" +
        "**.....*\n" +
        "..*....*.*\n" +
        "....**..*\n" +
        "....**\n" +
        "",

        shickengine :

        "#Life 1.05\n" +
        "#D Name: Schick engine\n" +
        "#D Author: Paul Schick\n" +
        "#D An orthogonal c/2 tagalong found in 1972.\n" +
        "#D www.conwaylife.com/wiki/index.php?title=Schick_engine\n" +
        "#N\n" +
        "#P -11 -4\n" +
        "****\n" +
        "*...*\n" +
        "*\n" +
        ".*..*\n" +
        "#P -5 -2\n" +
        "..*\n" +
        ".*******\n" +
        "**.***..*\n" +
        ".*******\n" +
        "..*\n" +
        "#P -7 -1\n" +
        "*\n" +
        "#P -11 1\n" +
        ".*..*\n" +
        "*\n" +
        "*...*\n" +
        "****\n" +
        "#P -7 1\n" +
        "*\n" +
        "",

        trafficcircle :

        "#Life 1.05\n" +
        "#D Traffic circle from http://www.radicaleye.com/lifepage/picgloss/picgloss.html\n" +
        "#N\n" +
        "#P -25 -25\n" +
        "......................**....**..........................\n" +
        "......................*.*..*.*...................\n" +
        "........................*..*.....................\n" +
        ".......................*....*....................\n" +
        ".......................*....*....................\n" +
        ".......................*....*....................\n" +
        ".........................**.....**...............\n" +
        "................................***..............\n" +
        "................................**.*.............\n" +
        "..................................*.*............\n" +
        "..........................***....*..*............\n" +
        "..................................**.............\n" +
        "..........**............*.....*..................\n" +
        ".........*..*...........*.....*..................\n" +
        ".......*..*.*...........*.....*..................\n" +
        "...........*.....................................\n" +
        ".......*.**...............***....................\n" +
        "........*.....*..................................\n" +
        "..............*..................................\n" +
        ".**...........*..................................\n" +
        ".*..***..........................................\n" +
        "..**......***...***............................**\n" +
        ".......*...................................***..*\n" +
        ".......*......*...............................**.\n" +
        "..**..........*........*..................*......\n" +
        ".*..***.......*......**.**............*...*......\n" +
        ".**....................*............**.**.....**.\n" +
        "......................................*....***..*\n" +
        "...............................................**\n" +
        ".................................................\n" +
        ".......................................*.*.......\n" +
        ".....................***..................*......\n" +
        "......................................*..*.......\n" +
        "...................*.....*...........*.*.*.......\n" +
        "...................*.....*...........*..*........\n" +
        "...................*.....*............**.........\n" +
        "..............**.................................\n" +
        ".............*..*....***.........................\n" +
        ".............*.*.*...............................\n" +
        "..............*.***..............................\n" +
        "................***..............................\n" +
        ".......................**........................\n" +
        ".....................*....*......................\n" +
        ".....................*....*......................\n" +
        ".....................*....*......................\n" +
        "......................*..*.......................\n" +
        "....................*.*..*.*.....................\n" +
        "....................**....**.....................\n" +
        "",

        highlifeglidergun :

        "#Life 1.05\n" +
        "#D Period 96 replicator based glider gun by David Bell.\n" +
        "#D --- The smallest known glider gun based on replicators.\n" +
        "#D A block perturbs the replicator to produce the glider,\n" +
        "#D while a period 2 clock oscillator prevents a spark \n" +
        "#D from being formed that would modify the block.  \n" +
        "#D One glider is shown where it was just created.\n" +
        "#D From HighLife - An Interesting Variant of Life \n" +
        "#D (part 1/3) by David I. Bell, dbell@canb.auug.org.au\n" +
        "#D 7 May 1994\n" +
        "#R 23/36\n" +
        "#P -18 -14\n" +
        "**...................................\n" +
        "**...................................\n" +
        "..............*......................\n" +
        ".............***.....................\n" +
        "............**.**....................\n" +
        "...........**.**.....................\n" +
        "..........**.**......................\n" +
        "...........***.......................\n" +
        "............*........................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".....................................\n" +
        ".........................**......**..\n" +
        "........................*.*......**..\n" +
        "..........................*..........\n" +
        ".....................................\n" +
        "...................................*.\n" +
        ".................................*.*.\n" +
        "..................................*.*\n" +
        ".........................**.......*..\n" +
        ".........................**..........\n" +
        "#P -5 15\n" +
        "..**\n..*\n" +
        "*.*\n" +
        "**\n" +
        ""
    } ;
}


//=========================================== Game of Life Member Functions:  File Reading ===========================================

// Read a Game of Life file in 1.05 format.
//
// Use a recursive descent parser, similar to awk parser from
//        THE AWK PROGRAMMING LANGUAGE, Aho, Kernighan, Weinberger, pgs. 147-152.
//
// Here is an explanation for the Life 1.05 format from
//
//     http://www.mirekw.com/ca/ca_files_formats.html
//
// This ASCII format just draws the pattern with "." and "*" symbols. The line length should not
// exceed 80 characters.
//
// The "#Life" line is followed by optional description lines, which begin with "#D" and are
// followed by no more than 78 characters of text. Leading and trailing spaces are ignored,
// so the following two "#D" lines are equivalent:
//
//     #D This is a Description line
//     #D     This is a Description line
//     There should be no more than 22 "#D" lines in a .LIF file.
//
// Next comes an optional rule specification. If no rules are specified, then the pattern will
// run with whatever rules the Life program is currently set to. The patterns in the collection
// here enforce "Normal" Conway rules using the "#N" specifier. Alternate rules use
// "#R" ("#N" is exactly the same as "#R 23/3"). Rules are encoded as Survival/Birth,
// each list being a string of digits representing neighbor counts. Since there are exactly
// eight possible neighbors in a Conway-like rule, there is no need to separate the digits,
// and "9" is prohibited in both lists. For example,
//
//     #R 125/36
//
// means that the pattern should be run in a universe where 1, 2, or 5 neighbors are necessary
// for a cell's survival, and 3 or 6 neighbors allows a cell to come alive.
//
// Next come the cell blocks. Each cell block begins with a "#P" line, followed by "x y"
// coordinates of the upper-left hand corner of the block, assuming that 0 0 is the center
// of the current window to the Life universe.
//
// This is followed by lines that draw out the pattern in a visual way, using the "." and "*"
// characters (off, on). Each line must be between 1 and 80 characters wide, inclusive;
// therefore, a blank line is represented by a single dot, whereas any other line may truncate
// all dots to the right of the last "*". There is no limit to the number of lines in a cell block.
//
// Any line of zero length (just another carriage return) is completely ignored. Carriage returns
// are MSDOS-style (both 10 and 13).
//
// For example, a glider in Life1.05 format is saved as:
//
//     #Life 1.05
//
//     ***
//     *..
//     .*.
//
// Life 1.05 format was designed to be easily ported. You can just look at a pattern in this format
// in a text editor, and figure out what it is.
//
// See also http://www.conwaylife.com/wiki/Life_1.05
//
gameOfLife.readLifeFile = function( fileText )
{
    let lineOfFile = null ;

    // Create a function to return the next line of the file.
    let readLine = make_readNextLine( fileText ) ;

    // Read the file, catching any exceptions thrown during the read.
    try
    {
        // Eat the version number.
        this.parseVersionNumber( readLine() ) ;

        // Read comment lines.
        let numCommentLines = 0 ;
        while (this.parseCommentLine( lineOfFile = readLine() ))
        {
            this.gameBoard.comment[ numCommentLines ] = lineOfFile ;

            if (++numCommentLines > this.gameBoard.maxNumCommentLines)
                throw RangeError( "too many comment lines " + numCommentLines + " > " + this.gameBoard.maxNumCommentLines ) ;
        }
        this.gameBoard.numCommentLines = numCommentLines ;

        // Read the optional rules line.
        let rules = this.parseRules( lineOfFile ) ;
        if (rules)
        {
            // It was a rules line, so fetch the next line.
            this.gameBoard.rules.survival = rules[ 0 ] ;
            this.gameBoard.rules.birth    = rules[ 1 ] ;
            lineOfFile = readLine() ;
        }
        else
        {
            // It wasn't a rules line:  just use the Conway rules.
            this.gameBoard.rules.survival = { numRules : 2, numNeighbors : [ 2, 3, , , , , , , ] } ;
            this.gameBoard.rules.birth    = { numRules : 1, numNeighbors : [ 3,  , , , , , , , ] } ;
        }

        // Read sequences of life pattern locations and patterns.
        // End of file will throw an exception to break us out of the loop.
        for(;;)
        {
            // Pattern location.
            let patternLocation = this.parsePatternLocation( lineOfFile ) ;

            if (!patternLocation)
                throw SyntaxError( "cannot parse pattern location line " + lineOfFile ) ;

            // Rows of pattern lines.
            let patternRow = 0 ;
            while (this.parsePatternLine( lineOfFile = readLine(), patternLocation, patternRow, this.gameBoard ))
                ++patternRow ;
        }
    }
    catch( e )
    {
        if (e instanceof RangeError)
        {
            // End of file (actually end of string).
            if (e.message === "end of file")
                return true ;
            // A real error!
            else
            {
                alert( "ERROR in reading file: " + e.message ) ;
                return false ;
            }
        }
        // Some error got thrown above when parsing the file.
        else if (e instanceof SyntaxError )
        {
            alert( "ERROR in reading file: " + e.message ) ;
            return false ;
        }
    }

    return true ;
}

// Return true if the version number of a line is Life 1.05
gameOfLife.parseVersionNumber = function( lineOfFile )
{
    if (!lineOfFile.match( /^#Life 1\.05/))
        throw  "life file version number " + lineOfFile + " is not 1.05"  ;
}

// Parse one line of a life file to see if it is a comment line.
// i.e. of the form
//     #D<sequence of characters>
gameOfLife.parseCommentLine = function( lineOfFile )
{
    if (lineOfFile.match( "^#D"))
        return true ;

    return false ;
}

// Parse a rules line.  There are two forms:
// (1) The normal Conway life rules
//          #N
// (2) Arbitrary rule where we list d1 ... neighbors for survival and D1 ... neighbors for a birth.
//          #R d1 d2 ... / D1 D2 ...
//     e.g. the Conway rules are encoded as
//          #R 23/3.
//     specifes number of neighbors for survival is 2 or 3 and number for a birth is 3.
gameOfLife.parseRules = function( lineOfFile )
{
    let survival, birth ;

    // Return if we don't see a rules line.
    if (!lineOfFile.match( /^\s*#[NR]/ ))
        return null ;

    // Normal Conway rules.
    if (lineOfFile.match( /^\s*#N/ ))
    {
        survival = { numRules : 2, numNeighbors : [ 2, 3, , , , , , , ] } ;  // Empty entries are undefined.
        birth    = { numRules : 1, numNeighbors : [ 3,  , , , , , , , ] } ;
        return [ survival, birth ] ;
    }

    // Other rules of the type #R single digit list of neighbors for survivals / ... for births.
    let rulePattern = /^\s*#R\s*(\d+)\/(\d+)/ ;

    // List ought to have three pieces, the match and two strings of digits:  [ "#R 23/3", "23", "3" ].
    let rulesString = lineOfFile.match( rulePattern ) ;
    if (rulesString === null || rulesString.length != 3)
        return null ;

    return [ this.parseRulesList( rulesString[ 1 ] ), this.parseRulesList( rulesString[ 2 ] ) ] ;
}

// Parse a rules list into a rules object.
gameOfLife.parseRulesList = function( rulesString )
{
    // Count survivals.
    let neighborCountsString = rulesString ;
    let numNeighbors = Array( 9 ) ;
    let numRules = rulesString.length ;

    for (let i = 0 ;  i < numRules ;  ++i)
        numNeighbors[ i ] = parseInt( neighborCountsString.charAt( i ) ) ;

    let rules = 
    {
        numNeighbors : numNeighbors,
        numRules     : numRules
    }
    return rules ;
}

// Parse one line of a life file to see if it is a cell block
// of the form
//     #P <integer x coordinate> <integer y coordinate>
// Coordinates can have optional + or - in front, whitespace delimiters.
// e.g.
//     #P -2 2
gameOfLife.parsePatternLocation = function( lineOfFile )
{
    let rulePattern = /^\s*#P\s*([+-]*\d+)\s*([+-]*\d+)/ ;

    // List ought to have three pieces, the match and two digits.
    let patternString = lineOfFile.match( rulePattern ) ;
    if (patternString === null || patternString.length != 3)
        return null ;

    // Return the x and y coordinates.
    let point = { x:0, y:0 } ;
    point.x = parseInt( patternString[ 1 ] ) ;
    point.y = parseInt( patternString[ 2 ] ) ;
    return point ;
}

// Parse one line of a life file to see if it is a pattern line of the form of * or .   e.g.
//
//    ...*
//    ....*
//    ....*
//    .****
//
// Any other character other than whitespace is an error.  Fill in the game board while parsing.
// If we go outside the bounds of the game board, throw an error.
gameOfLife.parsePatternLine = function( lineOfFile, patternLocation, patternRow, gameBoard )
{
    //  Middle row of the game board.
    let centerRow = gameBoard.numRows / 2 ;
    let centerCol = gameBoard.numCols / 2 ;

    //  Fill in occupied cells in the game board.
    for (let col = 0 ; col < lineOfFile.length ;  ++col)
    {
        let counter = lineOfFile.charAt( col ) ;

        // Record an occupied cell in the game board.
        if (counter === "*")
        {
            // Counter is offset by cell block upper left corner
            // coordinates and by row number of the pattern line.
            counterCol = centerCol + patternLocation.x + col ;
            counterRow = centerRow + patternLocation.y + patternRow ;

            //  Out of bounds counter check.
            if (counterRow < 0 || counterRow >= gameBoard.numRows ||
                counterCol < 0 || counterCol >= gameBoard.numCols)
            {
                throw "Game pattern out of bounds at pattern location row " + patternLocation.y + " col " + patternLocation.x +
                       " at counter row " + counterRow + " col " + counterCol ;
            }

            //  Flip the counter occupancy flag.
            gameBoard.cell[ counterRow ][ counterCol ].occupied = Occupancy.Occupied ;
        }
        // Ignore . or whitespace.
        else if (counter === "." || counter === " " || counter === "\r" || counter === "\t" || counter === "\n" )
            ;
        // Don't expect any other characters.
        else
            return false ;
    }

    return true ;
}

//=========================================== Game of Life Member Functions:  File Writing ===========================================

// Write the life game board to file..
gameOfLife.writeLifeFile = function( gameBoard )
{
    let fileText = "#Life 1.05\n" ;

    // Write out comments.
    for (let row = 0 ;  row < gameBoard.numCommentLines ;  ++row)
        fileText += (gameBoard.comment[ row ] + "\n") ;

    // These are the John Horton Conway default life rules.
    if (gameBoard.rules.birth.numRules             === 1 &&
        gameBoard.rules.birth.numNeighbors[ 0 ]    === 3 &&
        gameBoard.rules.survival.numRules          === 2 &&
        gameBoard.rules.survival.numNeighbors[ 0 ] === 2 &&
        gameBoard.rules.survival.numNeighbors[ 1 ] === 3)
    {
        // Write the normal rules line.
        fileText += "#N\n" ;
    }
    // Write the full rules line.
    else
    {
        fileText += "#R " ;

        //  Write the survival rules first.
        for (let i = 0 ;  i < gameBoard.rules.survival.numRules ; ++i)
            fileText += gameBoard.rules.survival.numNeighbors[ i ] ;

        fileText += "/" ;

        //  Write the birth rules.
        for (let i = 0 ;  i < gameBoard.rules.birth.numRules ; ++i)
            fileText += gameBoard.rules.birth.numNeighbors[ i ] ;

        fileText += "\n" ;
    }

    // Find all the connected components in the game board.
    let boundingBoxes = this.traverseGameBoard( gameBoard ) ;

    // Split boxes which are too wide.
    for (let i = 0 ;  i < boundingBoxes.length ;  ++i)
    {
        let box = boundingBoxes[ i ] ;

        //  Box is too wide.
        if (box.right - box.left > this.GameSettings.MaxFileLineLength)
        {
            // Split off the left piece.
            boundingBoxes[ i ].left   = box.left ;
            boundingBoxes[ i ].top    = box.top ;
            boundingBoxes[ i ].bottom = box.bottom ;
            boundingBoxes[ i ].right  = box.left + this.GameSettings.MaxFileLineLength - 1 ;

            // Split off the right piece, which may still be too large, and append it
            // to the end, where it will be processed later.
            let boxRight = [] ;
            boxRight.left   = box.left + this.GameSettings.MaxFileLineLength ;
            boxRight.top    = box.top ;
            boxRight.bottom = box.bottom ;
            boxRight.right  = box.right ;
            boundingBoxes.push( boxRight ) ;
        }
    }

    //  Middle of the game board.
    let centerRow = gameBoard.numRows / 2 ;
    let centerCol = gameBoard.numCols / 2 ;

    // Now that we have all the bounding boxes, write the pattern blocks.
    for (i = 0 ;  i < boundingBoxes.length ;  ++i)
    {
        let box = boundingBoxes[ i ] ;

        // Write out the pattern upper left corner offset from game board center.
        let patternRow = box.top  - centerRow ;
        let patternCol = box.left - centerCol ;
        fileText += ("#P " + patternCol + " " + patternRow + "\n") ;

        // Write out rows of patterns for this block.
        for (let row = box.top ;  row <= box.bottom ;  ++row)
            fileText += this.createPatternLine( box, row ) ;
    }

    return fileText ;
}

// Label all the clusters of counters in the game board.
gameOfLife.traverseGameBoard = function()
{
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    //  Clear the game board connectivity information in all cells (zero all labels, unmark all edges, zero all father links).
    for (let row = 0 ;  row < numRows ;  ++row)
    {
        for (let col = 0 ;  col < numCols ;  ++col)
        {
            this.gameBoard.cell[ row ][ col ].label  =  0 ;
            this.gameBoard.cell[ row ][ col ].edge   =  0 ;
            this.gameBoard.cell[ row ][ col ].father =  0 ;
        }
    }

    // Label all cells in the game board and return an array of bounding boxes for all clusters.
    let startLabel = 1 ;
    let boundingBoxes = [] ;

    for (let row = 0 ;  row < numRows ;  ++row)
    {
        for (let col = 0 ;  col < numCols ;  ++col)
        {
            //  Cell is occupied but not labelled.  Find its cluster and return the bounding box.
            if (this.gameBoard.cell[ row ][ col ].occupied === Occupancy.Occupied && this.gameBoard.cell[ row ][ col ].label === 0)
            {
                boundingBoxes.push( this.depthFirstTraversal( row, col, startLabel++ ) ) ;
            }
            // Else skip over the cell because it is labelled already or is empty, i.e. it is a background cell.
        }
    }

     return boundingBoxes ;
}

// Starting from (row, col) in the game board at an occupied cell,
// label the cluster of cells connected to it, and return a bounding
// box for the cluster.
gameOfLife.depthFirstTraversal = function( row, col, label )
{
    // Size of game board.
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    // Label this cell as the starting cell.
    this.gameBoard.cell[ row ][ col ].label = -1 ;

    // Bounding box is at least one cell's dimensions.
    let boundingBox =
    {
        top    : row,
        bottom : row,
        left   : col,
        right  : col
    } ;

    let nextRow ;
    let nextCol ;

    for (;;)
    {
        //  Find the next unmarked edge.
        let edge = this.nextUnmarkedEdge( row, col ) ;

        // If there is an unmarked edge, investigate this direction.
        if (edge > 0)
        {
            // Get the location of the next cell.
            [nextRow, nextCol] = this.nextCell( row, col, edge ) ;

            // Mark the edge of the current and next cell.
            this.markEdges( row, col, nextRow, nextCol, edge ) ;

            // The next cell is occupied and unlabeled and on the game board.
            if ( (nextRow < numRows && nextCol < numCols && 0 <= nextRow && 0 <= nextCol) &&
                this.gameBoard.cell[ nextRow ][ nextCol ].occupied === Occupancy.Occupied &&
                this.gameBoard.cell[ nextRow ][ nextCol ].label    === 0)
            {
                //  Record the father of the cell.
                this.gameBoard.cell[ nextRow ][ nextCol ].father =
                    this.encodeFather( nextRow, nextCol, row, col ) ;

                //  Label the cell.
                this.gameBoard.cell[ nextRow ][ nextCol ].label = label ;

                //  Record the maximum excursions for the bounding box.
                boundingBox.top    = Math.min( boundingBox.top,    nextRow ) ;
                boundingBox.bottom = Math.max( boundingBox.bottom, nextRow ) ;
                boundingBox.left   = Math.min( boundingBox.left,   nextCol ) ;
                boundingBox.right  = Math.max( boundingBox.right,  nextCol ) ;

                //  Step to the next cell.
                row = nextRow ;  col = nextCol ;
            }
            //  Rebound:  New cell was either already labelled or unoccupied,
            //  Pretend we've traversed the edge twice.
            //  NOTE:  We treat cells off the gameboard as unoccupied.
            //  We'll sometimes break apart clusters which would have been
            //  connected on our toroidal game board.
            //  But that just means we have more possible clusters;  the cells
            //  and their properties aren't affected.
            else ;
        }
        // All edges are marked.  Backtrack.
        else
        {
            //  We're back at the beginning.
            if (this.gameBoard.cell[ row ][ col ].label === -1)
            {
                //  Relabel the start label correctly.
                this.gameBoard.cell[ row ][ col ].label = label ;
                break ;
            }

            //  Backtrack along a father edge.
            edge = this.gameBoard.cell[ row ][ col ].father ;
            [row, col] = this.nextCell( row, col, edge ) ;
        }
    } // end forever loop

    return boundingBox ;
}

// In the next few functions, we will be encoding edges at a vertex by bitmaps.  The encoding is
//
//    8  4  2
//     \ | /
//  16 - C - 1
//     / | \
//   32 64 128

// Return the first unmarked edge in a counterclockwise scan starting from the right edge.
// e.g. if edge = 11110011, next unmarked edge returns 4.
gameOfLife.nextUnmarkedEdge = function( row, col )
{
    let mask = 1 ;
    let edge = this.gameBoard.cell[ row ][ col ].edge ;

    for (let bit = 0 ;  bit < 8 ;  ++bit)
    {
        if ((mask & edge) === 0)
            return mask ;
        mask <<= 1 ;
    }

    return 0 ; // No unmarked edges.
}

// Mark the edge of a cell at (row, col) in the game board in the direction
// (row, col) to (nextRow, nextCol).  Also mark the edge at (nextRow, nextCol)
// in the direction to (row, col).
gameOfLife.markEdges = function( row, col, nextRow, nextCol, edge )
{
    let numRows = this.gameBoard.numRows ;
    let numCols = this.gameBoard.numCols ;

    // Mark the edge from (row, col) to (nextRow, nextCol).
    this.gameBoard.cell[ row ][ col ].edge |= edge ;

    // Encode and mark the edge from the other direction:  from (nextRow, nextCol) to (row, col).
    let oppositeEdge = 0 ;
    switch( edge )
    {
        case   0: oppositeEdge =   0 ; break ;
        case   1: oppositeEdge =  16 ; break ;
        case   2: oppositeEdge =  32 ; break ;
        case   4: oppositeEdge =  64 ; break ;
        case   8: oppositeEdge = 128 ; break ;
        case  16: oppositeEdge =   1 ; break ;
        case  32: oppositeEdge =   2 ; break ;
        case  64: oppositeEdge =   4 ; break ;
        case 128: oppositeEdge =   8 ; break ;
        default: break ;
    }

    // But only mark the edge if it is within the game board.
    if (nextRow < numRows && nextCol < numCols && 0 <= nextRow && 0 <= nextCol)
        this.gameBoard.cell[ nextRow ][ nextCol ].edge |= oppositeEdge ;
}

// Given a cell at (row, col) in the game board and an edge direction, edge,
// find the next cell location at the other end of the edge.
// Note from above, we don't mark edges which cause us to move outside the gameboard.
gameOfLife.nextCell = function( row, col, edge )
{
    let nextRow = nextCol = 0 ;

    switch( edge )
    {
        case   1: nextRow = row     ;  nextCol = col + 1 ;  break ;
        case   2: nextRow = row - 1 ;  nextCol = col + 1 ;  break ;
        case   4: nextRow = row - 1 ;  nextCol = col     ;  break ;
        case   8: nextRow = row - 1 ;  nextCol = col - 1 ;  break ;
        case  16: nextRow = row     ;  nextCol = col - 1 ;  break ;
        case  32: nextRow = row + 1 ;  nextCol = col - 1 ;  break ;
        case  64: nextRow = row + 1 ;  nextCol = col     ;  break ;
        case 128: nextRow = row + 1 ;  nextCol = col + 1 ;  break ;
        default: break ;
    }

    return [ nextRow, nextCol ] ;
}

// Encode an edge so that nextCell() will take us to the father from the son.
gameOfLife.encodeFather = function( sonRow, sonCol, fatherRow, fatherCol )
{
    let edge ;
    let rowChange = fatherRow - sonRow ;
    let colChange = fatherCol - sonCol ;

    if      (rowChange ===  0 && colChange ===  1)  edge =   1 ;
    else if (rowChange === -1 && colChange ===  1)  edge =   2 ;
    else if (rowChange === -1 && colChange ===  0)  edge =   4 ;
    else if (rowChange === -1 && colChange === -1)  edge =   8 ;
    else if (rowChange ===  0 && colChange === -1)  edge =  16 ;
    else if (rowChange ===  1 && colChange === -1)  edge =  32 ;
    else if (rowChange ===  1 && colChange ===  0)  edge =  64 ;
    else if (rowChange ===  1 && colChange ===  1)  edge = 128 ;
    else edge = 0 ;

    return edge ;
}

// Generate one pattern line of "*" and "." characters to represent occupied and empty cells at row, given the bounding box coordinates.
gameOfLife.createPatternLine = function(  box, row )
{
    let lineOfFile = "" ;
    let lastCol = box.right ;

    // Find the last occupied cell in the row.
    for ( ;  lastCol >= box.left ;  --lastCol)
        if (this.gameBoard.cell[ row ][ lastCol ].occupied === Occupancy.Occupied)
            break ;

    // Convert occupied cells to "*" and unoccupied to "."
    for (let col = box.left ; col <= lastCol ;  ++col)
    {
        if (this.gameBoard.cell[ row ][ col ].occupied === Occupancy.Occupied)
            lineOfFile += "*" ;
        else
            lineOfFile += "." ;
    }

    lineOfFile += "\n" ;

    return lineOfFile ;
}

//===================================================== Callback Closure Functions ===================================================

// Make callback functions which we can register with event handlers.
//
// We pass in event information through the callback function argument.
// Closures give us permanent access the entire game state. 
//
// For example, make_cycleGame( gameOfLifeApp ) returns an anonymous inner function foo( e ), then goes out of scope.
// However, foo( e ) has permanent access to its surrounding environment, which contains the gameOfLifeObject.
// Thus foo( e ) function can always access gameOfLifeApp.cycleGame() in particular.
//
// Note that what's passed by value in the maker function argument is a reference to gameOfLifeApp, not a copy of the object.  
// The inner function can read and write the app's member variables from now on, after make_cycleGame() returns.

// Manufacture a callback function to single step the game to be called from the timer or directly from the GUI.
function make_cycleGame( gameOfLifeApp )
{
    return function( e )
    {
        gameOfLifeApp.cycleGame() ;
    } ;
}

// Manufacture a callback function to be called whenever the mouse is in the canvas and we click it.
function make_onCanvasMouseClick( gameOfLifeApp )
{
    return function( e )
    {
        let pos = gameOfLifeApp.gameBoard.canvasToCellCoord( gameOfLifeApp.gameBoard.getCursorPosition( e )) ;
        gameOfLifeApp.gameBoard.toggleCounter( pos ) ;
    } ;
}

// Manufacture a callback function when the mouse is moved over the canvas.
function make_onCanvasMouseMove( gameOfLifeApp )
{
    return function( e )
    {
        // Show the cell (row, col) position.
        let pos = gameOfLifeApp.gameBoard.canvasToCellCoord( gameOfLifeApp.gameBoard.getCursorPosition( e )) ;

        // Show the complete cell state.
        let row = pos[ 0 ] ;
        let col = pos[ 1 ] ;

        // Cursor gives a game board position out of bounds.
        if (row >= 0 && col >= 0 && row < gameOfLifeApp.GameSettings.GameBoardNumRows && col < gameOfLifeApp.GameSettings.GameBoardNumCols)
        {
            let state = gameOfLifeApp.gameBoard.cell[ row ][ col ].state ;

            gameOfLifeApp.GameOfLifeCellState.innerHTML =
                  " row/col: "       + row + " " + col +
                  " occupied: "      + gameOfLifeApp.gameBoard.cell[ row ][ col ].occupied +
                  " occupied prev: " + gameOfLifeApp.gameBoard.cell[ row ][ col ].occupiedPreviously +
                  " num neighbors: " + gameOfLifeApp.gameBoard.cell[ row ][ col ].numberOfNeighbors +
                  " state: "         + state +
                  " age: "           + gameOfLifeApp.gameBoard.cell[ row ][ col ].age +
                  " label: "         + gameOfLifeApp.gameBoard.cell[ row ][ col ].label +
                  " father: "        + gameOfLifeApp.gameBoard.cell[ row ][ col ].father +
                  " edge: "          + gameOfLifeApp.gameBoard.cell[ row ][ col ].edge ;
        }
    } // end func
}

// Callback function to load a new life pattern.
function make_loadSampleLifePattern( gameOfLifeApp )
{
    return function( e )
    {
        let option = e.target.value ;

        gameOfLifeApp.gameBoard.clearGameState() ;
        gameOfLifeApp.readLifeFile( gameOfLifeApp.sampleLifePatterns[ option ] ) ;
        gameOfLifeApp.gameBoard.updateView() ;
        gameOfLifeApp.updateRulesView() ;
    }
}

// Manufacture a callback function to be called from a form on a file selection.
function make_GameOfLifeLoadFile( gameOfLifeApp )
{
    return function( e )
    {
        // The target is the object which this event was dispatched on.
        // It contains a list of files.
        let files = e.target.files ;

        // Loop through the FileList.
        for (let i = 0, f; f = files[i]; i++)
        {
            // Only process Game of Life files.
            if ( !f.name.match("\.lif"))
                continue ;

            let reader = new FileReader() ;

            // Callback function for file load completion.
            // Use lispish closure to encapsulate the reader.result which is the file contents.
            // Then call the inner function with the file contents.
            reader.onload = function()
            {
                gameOfLifeApp.GameOfLifeClipboard.value = reader.result ;

                // Clear out the game board, load the file, update the gameboard view, status and rules.
                gameOfLifeApp.gameBoard.clearGameState() ;
                gameOfLifeApp.readLifeFile( reader.result ) ;
                gameOfLifeApp.gameBoard.updateView() ;
                gameOfLifeApp.updateRulesView() ;
            } ;

          // Read in the image file text.
          reader.readAsText( f, "UTF-8" ) ;
        } // for
    } // function
}

// Manufacture a function to print debug information.
function make_debugPrint( gameOfLifeApp )
{
    return function( option )
    {
        let text = gameOfLifeApp.GameOfLifeDebug.innerHTML ;

        switch( option )
        {
            case gameOfLifeApp.DebugPrintOptions.GameBoard:
                // Clear the debug area when printing the gameboard.
                text = "" ;
                text += gameOfLifeApp.printGameBoard( gameOfLifeApp.gameBoard ) ;
            break ;

            case gameOfLifeApp.DebugPrintOptions.Neighbors:
                text += gameOfLifeApp.printNeighborCounts( gameOfLifeApp.gameBoard ) ;
            break ;

            case gameOfLifeApp.DebugPrintOptions.States:
                text += gameOfLifeApp.printCounterState( gameOfLifeApp.gameBoard ) ;
            break ;
        }

        // Write out the text to the debug area.
        gameOfLifeApp.GameOfLifeDebug.innerHTML = text ;

    } // inner function
}

// Create a closure which returns the next line of text.
function make_readNextLine( fileText )
{
    // Split text of the entire file into lines.
    let linesOfFile    = fileText.split( "\n" ) ;
    let numLinesInFile = linesOfFile.length ;

    let lineNum = 0 ;

    // Returns the next line of the file.
    return function()
    {
        if (lineNum < numLinesInFile)
            return linesOfFile[ lineNum++ ] ;
        else
            throw RangeError( "end of file" ) ;
    }
}

// Not currently used...
function supportsLocalStorage()
{
    // window is the default JavaScript global for the web page.
    return ("localStorage" in window) && window["localStorage"] !== null ;
}

function writeClipboardToLocalStorage( file )
{
    if (!supportsLocalStorage())
        return false;

    localStorage[ "GameOfLife.file.name" ] = file ;

    return true;
}

function readLocalStorageToClipboard()
{
    if (!supportsLocalStorage())
        return false;

    file = localStorage[ "GameOfLife.file.name" ] ;

    if (!file)
        return null ;

    return file ;
}

//================================================ Game Board Members ========================================================================

gameBoard.init = function( GameSettings, debugPrint, DebugPrintOptions, GameOfLifeCanvas, GameOfLifeState )
{
    // Access the canvas from the game board.
    this.GameOfLifeCanvas = GameOfLifeCanvas ;
    this.widthPixels      = GameOfLifeCanvas.width ;
    this.heightPixels     = GameOfLifeCanvas.height ;
    this.graphicsContext  = GameOfLifeCanvas.getContext( "2d" ) ;

    // Access the game state display area.
    this.GameOfLifeState = GameOfLifeState ;

    // Copy over debug print and its options to the game board.
    this.DebugPrintOptions = DebugPrintOptions ;
    this.debugPrint = debugPrint ;
    this.GameSettings = GameSettings ;

    // Initialize game board size.
    this.numRows    = this.GameSettings.GameBoardNumRows ;
    this.numCols    = this.GameSettings.GameBoardNumCols ;

    // Initialize game board global state.
    this.population = 0 ;
    this.generation = 0 ;

    // Normal Conway rules:  a counter survives if it has 2 or 3 neighbors else dies of loneliness;
    // an empty cell with 3 neighbors has a birth.
    this.rules =
    {
        survival : undefined,
        birth    : undefined
    } ;

    this.rules.survival =
    {
        numRules     :   2,
        numNeighbors : [ 2, 3, , , , , , , ]
    } ;

    this.rules.birth =
    {
        numRules     :   1,
        numNeighbors : [ 3, , , , , , , , ]
    } ;

    // Generate the game board as an array of rows, where each row is an array of columns,
    // and each element is a cell.
    this.cell = Array( this.numRows ) ;
    for (let row = 0 ;  row < this.numRows ;  ++row)
        this.cell[ row ] = Array( this.numCols ) ;

    // Fill each cell in the game board with default values.
    for (let col = 0 ;  col < this.numCols ;  ++col)
    {
        for (let row = 0 ;  row < this.numRows ;  ++row)
        {
            this.cell[ row ][ col ] = Object.create( Object.prototype, 
            {
                // A single empty game board cell and its default state.
                // Each variable in this object has a bunch of properties.
                //     writeable - we can change the value of numberOfNeighbors with an assignement operator.
                //     enumerable - we can use numberOfNeighbors in a for..in loop or access via Object.keys()
                //     configurable - we can change the data type and other attributes of numberOfNeighbors and we can delete it.
                //     value - initial value upon object creation.
                //     We don't need any get() or set() properties.
		numberOfNeighbors:  { value:  0, 			writable: true, enumerable: true, configurable: true, },// No neighbors.
		occupied:           { value:  Occupancy.Empty, 		writable: true, enumerable: true, configurable: true, },// Not occupied
		occupiedPreviously: { value:  Occupancy.Indeterminate,  writable: true, enumerable: true, configurable: true, },// No previous occupation.
		state:              { value:  State.Indeterminate, 	writable: true, enumerable: true, configurable: true, },// No state.
		age:                { value:  0, 			writable: true, enumerable: true, configurable: true, },// Cell is new.
		// For traversal only.
		label:              { value: -1, writable: true, enumerable: true, configurable: true, },// Cell is unlabelled.
		father:             { value: -1, writable: true, enumerable: true, configurable: true, },// Cell has no father.
		edge:               { value: -1, writable: true, enumerable: true, configurable: true, },// Edges are unmarked.
            } ) ;
        }
    }

    // Comments.
    this.maxNumCommentLines = GameSettings.MaxNumCommentLines ;
    this.comment            = Array( GameSettings.MaxNumCommentLines ) ;
    this.numCommentLines    = GameSettings.MaxNumCommentLines ;

    //  Leave space for blank comment lines.
    for (let row = 0 ;  row < GameSettings.MaxNumCommentLines ;  ++row)
        this.comment[ row ] = "#D" ;
}

//===================================================== Game Board State Functions ===================================================

// Update the game board to go from one generation to the next.
gameBoard.updateGameBoard = function()
{
    this.debugPrint( this.DebugPrintOptions.GameBoard ) ;

    // Count the number of neighbors for each counter.
    this.countNeighbors() ;

    // Apply the life rules to see who lives and dies.
    this.birthAndDeath() ;

    this.debugPrint( this.DebugPrintOptions.Neighbors ) ;
    this.debugPrint( this.DebugPrintOptions.States ) ;

    // We now have a new generation.
    ++this.generation ;
}

// If a cell is occupied, update the neighbor counts for all adjacent cells.
// Treat the boundary of the board specially.
gameBoard.countNeighbors = function()
{
    //  Size of game board.
    let numRows = this.numRows ;
    let numCols = this.numCols ;

    //  Zero out the neighbor count for each cell.
    for (let row = 0 ;  row < numRows ;  ++row)
        for (let col = 0 ;  col < numCols ;  ++col)
            this.cell[ row ][ col ].numberOfNeighbors = 0 ;

    // Update neighbor counts for counters in first and last columns.
    for (let row = 0 ;  row < numRows ;  ++row)
    {
        if (this.cell[ row ][ 0 ].occupied === Occupancy.Occupied)
            this.boundaryNeighborCount( row, 0 ) ;

        if (this.cell[ row ][ numCols - 1 ].occupied === Occupancy.Occupied)
            this.boundaryNeighborCount( row, numCols - 1 ) ;
    }

    // Update neighbor counts for counters in the first and last rows,
    // skipping the corners since these have already been updated.
    for (let col = 1 ;  col <= numCols-2 ;  ++col)
    {
        if (this.cell[ 0 ][ col ].occupied === Occupancy.Occupied)
            this.boundaryNeighborCount( 0, col ) ;

        if (this.cell[ numRows - 1 ][ col ].occupied === Occupancy.Occupied)
            this.boundaryNeighborCount( numRows - 1, col ) ;
    }

    // Update neighbor counts on interior cells.
    for (let row = 1 ;  row <= numRows - 2 ;  ++row)
    {
        for (let col = 1 ;  col <= numCols - 2 ;  ++col)
        {
            //  Current cell is occupied.
            if (this.cell[ row ][ col ].occupied === Occupancy.Occupied)
            {
                //  Update neighbor count for all its 8 adjacent cells.
                ++this.cell[ row - 1 ][ col - 1 ].numberOfNeighbors ;
                ++this.cell[ row - 1 ][ col     ].numberOfNeighbors ;
                ++this.cell[ row - 1 ][ col + 1 ].numberOfNeighbors ;

                ++this.cell[ row     ][ col - 1 ].numberOfNeighbors ;
                ++this.cell[ row     ][ col + 1 ].numberOfNeighbors ;

                ++this.cell[ row + 1 ][ col - 1 ].numberOfNeighbors ;
                ++this.cell[ row + 1 ][ col     ].numberOfNeighbors ;
                ++this.cell[ row + 1 ][ col + 1 ].numberOfNeighbors ;
            }
        }
    }
}

// Given that the boundary cell at (row, col) is occupied, update the neighbor
// counts for all adjacent cells.
gameBoard.boundaryNeighborCount = function( row, col )
{
    let adjRow, adjCol, adjTorusRow, adjTorusCol ;

    // Iterate through all adjacent cells.
    for (adjRow = row - 1 ;  adjRow <= row + 1 ;  ++adjRow)
    {
        for (adjCol = col - 1 ;  adjCol <= col + 1 ;  ++adjCol)
        {
            adjTorusRow = adjRow ;
            adjTorusCol = adjCol ;

            //  Wrap around so that we are topologically on a torus.
            if (adjTorusRow <= -1)
                adjTorusRow = this.numRows - 1 ;

            if (adjTorusCol <= -1)
                adjTorusCol = this.numCols - 1 ;

            if (adjTorusRow >= this.numRows)
                adjTorusRow = 0 ;

            if (adjTorusCol >= this.numCols)
                adjTorusCol = 0 ;

            //  All neighbors of the current cell get incremented.
            ++this.cell[ adjTorusRow ][ adjTorusCol ].numberOfNeighbors ;
        }
    }

    //  Neighbor count for the cell itself was incremented above.
    //  Correct for this.
    --this.cell[ row ][ col ].numberOfNeighbors ;
}

// Sweep through all cells, updating their occupancy according to the birth
// and death rules.  Use each cell's neighbor count from the last cycle.
gameBoard.birthAndDeath = function()
{
    let caseOfSurvival, caseOfBirth, cell ;

    this.population = 0 ;

    for (let row = 0 ;  row < this.numRows ;  ++row)
    {
        for (let col = 0 ;  col < this.numCols ;  ++col)
        {
            // Access the current cell at row, col.
            let cell = this.cell[ row ][ col ] ;

            // Save the previous occupation state for this cell.
            cell.occupiedPreviously = cell.occupied ;

            caseOfBirth = caseOfSurvival = false ;

            //  An empty cell next to n1 or n2 or ... neighbors gets a birth.
            if (cell.occupied === Occupancy.Empty)
            {
                for (let i = 0 ; i < this.rules.birth.numRules ;  ++i)
                {
                    if (cell.numberOfNeighbors === this.rules.birth.numNeighbors[ i ])
                    {
                        caseOfBirth = true ;
                        cell.occupied = Occupancy.Occupied ;
                        cell.state    = State.Birth ;
                        cell.age      = 0 ;        // Cell is newborn.

                        // Early out since some rule allowed a birth.
                        break ;
                    }
                } // end for
            }
            else if (cell.occupied === Occupancy.Occupied)
            {
                for (i = 0 ; i < this.rules.survival.numRules ;  ++i)
                {
                    if (cell.numberOfNeighbors === this.rules.survival.numNeighbors[ i ])
                    {
                        caseOfSurvival = true ;

                        cell.state = State.Survival ;
                        ++cell.age ;                                 // Cell gets older.
                        if (cell.age > this.GameSettings.MaximumAge)   // Wrap around to nonzero.
                            cell.age = 1 ;

                        // Early out since some rule allowed a survival.
                        break ;
                    }
                } // end for

            }

            //  All other cases, including death from overpopulation, underpopulation
            //  and the case where the cell stays empty with no change.
            if (!caseOfSurvival && !caseOfBirth)
            {
                //  Occupied cell suffers death from overpopulation or underpopulation.
                if (cell.occupied === Occupancy.Occupied)
                {
                    cell.occupied = Occupancy.Empty ;
                    cell.state    = State.Death ;
                    cell.age      = 0 ;
                }
                // Empty cell does not change.
                else
                {
                    ++cell.age ;                                // Empty cell gets older.
                    if (cell.age > this.GameSettings.MaximumAge)  // Wrap around to nonzero.
                        cell.age = 1 ;
                }
            }

            // Update the population count.
            if (cell.occupied === Occupancy.Occupied)
                ++this.population ;
        } // end for col
    } // end for row
}

//===================================================== Drawing the Game Board =======================================================

gameBoard.drawLifeGrid = function()
{
    // White grid lines.
    this.graphicsContext.strokeStyle = "rgba(230,230,255,1.0)"

    // Erase the game board area.
    this.graphicsContext.clearRect( 0, 0, this.widthPixels, this.heightPixels ) ;

    // Get ready to draw lines.
    this.graphicsContext.beginPath();

    let cellWidth  = this.widthPixels  / this.numCols ;
    let cellHeight = this.heightPixels / this.numRows ;

    // Draw vertical lines.
    for (let x = 0 ;  x <= this.widthPixels ;  x += cellWidth)
    {
        this.graphicsContext.moveTo( 0.5 + x, 0 ) ;
        this.graphicsContext.lineTo( 0.5 + x, this.heightPixels ) ;
    }

    // Draw horizontal lines.
    for (let y = 0; y <= this.heightPixels ; y += cellHeight )
    {
        this.graphicsContext.moveTo( 0, 0.5 + y ) ;
        this.graphicsContext.lineTo( this.widthPixels, 0.5 + y ) ;
    }

    // Finish drawing.
    this.graphicsContext.stroke();
    this.graphicsContext.closePath() ;
}

// Canvas [x, y] to game board [row, col].
gameBoard.canvasToCellCoord = function( pos )
{
    let cellWidth  = this.widthPixels  / this.numCols ;
    let cellHeight = this.heightPixels / this.numRows ;

    let col = Math.floor( pos[0] / cellWidth  ) ;
    let row = Math.floor( pos[1] / cellHeight ) ;

    return [row, col] ;
}

// Game board [row, col]  to  canvas [x, y].
gameBoard.cellToCanvasCoord = function( pos )
{
    let cellWidth  = this.widthPixels  / this.numCols ;
    let cellHeight = this.heightPixels / this.numRows ;

    // Canvas (x,y) coordinates of the center of a cell.
    let x = cellWidth  * pos[1] + cellWidth  / 2 ;
    let y = cellHeight * pos[0] + cellHeight / 2 ;

    return [x, y] ;
}

gameBoard.getCursorPosition = function( e )
{
    // Mouse position is relative to the client window.  Subtract off the canvas
    // element position in the client window to get canvas coordinates, 
    // origin at top left corner.
    let canvasRect = this.GameOfLifeCanvas.getBoundingClientRect() ;
    let x = e.clientX - canvasRect.left ;
    let y = e.clientY - canvasRect.top ;

    // Correct when the canvas gets rescaled from its default size.
    let scaleX = this.GameOfLifeCanvas.width  / canvasRect.width ;
    let scaleY = this.GameOfLifeCanvas.height / canvasRect.height ;

    x *= scaleX ;
    y *= scaleY ;

    return [x, y] ;
}

// Toggle the counter state and redraw it.
gameBoard.toggleCounter = function( pos )
{
    let cell = this.cell[ pos[0] ][ pos[1] ] ;

    // Save the previous occupation state for this cell.
    cell.occupiedPreviously = cell.occupied ;

    //  If cell is empty, mark as occupied, or vice-versa.
    if (cell.occupied === Occupancy.Empty)
        cell.occupied = Occupancy.Occupied ;
    else if (cell.occupied === Occupancy.Occupied)
        cell.occupied = Occupancy.Empty ;

    this.drawCell( pos ) ;
}

// Draw the current cell.
gameBoard.drawCell = function( pos )
{
    //  Get the current cell information.
    let cell = this.cell[ pos[0] ][ pos[1] ] ;

    // Center canvas coordinates of cell.
    let centerOfCell = this.cellToCanvasCoord( pos ) ;

    let cellWidth  = this.widthPixels  / this.numRows ;
    let cellHeight = this.heightPixels / this.numCols ;
    let radius     = cellWidth / 2 - 0.8 ;

    // Cell occupation didn't change.  And of course, assume the board wasn't just cleared.
    if (cell.occupied === cell.occupiedPreviously && cell.occupied !== Occupancy.Indeterminate)
    {
        // Special case if an occupied cell just aged.
        if (cell.age === this.GameSettings.OldAge && cell.occupied === Occupancy.Occupied)
        {
            this.graphicsContext.beginPath();
            this.graphicsContext.fillStyle = "rgba( 185, 65, 64, 1.0 )" // Stable counter color:  red.
            this.graphicsContext.arc( centerOfCell[0], centerOfCell[1], radius, 0, Math.PI*2, true ) ;
            this.graphicsContext.fill();
            this.graphicsContext.closePath() ;
        }

        // Skip drawing.
        return ;
    }

    // If we are here, the cell occupation changed...

    // Cell is occupied:  draw the counter.
    if (cell.occupied === Occupancy.Occupied)
    {
        this.graphicsContext.beginPath();

        if( cell.age >= this.GameSettings.OldAge )
            this.graphicsContext.fillStyle = "rgba( 185, 65, 64, 1.0 )"    // Stable counter color:  red.
        else
            this.graphicsContext.fillStyle = "rgba(   0, 100, 255, 1.0 )"  // Active counter color:  blue.

        this.graphicsContext.arc( centerOfCell[ 0 ], centerOfCell[ 1 ], radius, 0, Math.PI * 2, true ) ;
        this.graphicsContext.fill();
        this.graphicsContext.closePath() ;
    }
    // Cell is empty:  erase the counter.
    else if (cell.occupied === Occupancy.Empty)
    {
        /// alert( "clear cell[ " + pos[0] +  " " + pos[1] + " ] = " + this.cell[ pos[0] ][ pos[1] ].occupied ) ;

        // Get the cell dimensions.
        let x1 = centerOfCell[ 0 ] - cellWidth  / 2 ;
        let y1 = centerOfCell[ 1 ] - cellHeight / 2 ;
        let x2 = centerOfCell[ 0 ] + cellWidth  / 2 ;
        let y2 = centerOfCell[ 1 ] + cellHeight / 2 ;

        // Erase the whole cell.
        this.graphicsContext.clearRect( x1, y1, cellWidth, cellHeight ) ;

        // White grid lines.
        this.graphicsContext.strokeStyle = "rgba(230,230,255,1.0)"

        // Redraw the lines of the cell.
        this.graphicsContext.beginPath();
        this.graphicsContext.moveTo( x1 + 0.5, y1       ) ; // Vertical
        this.graphicsContext.lineTo( x1 + 0.5, y2       ) ;

        this.graphicsContext.moveTo( x2 + 0.5, y1       ) ; // Vertical
        this.graphicsContext.lineTo( x2 + 0.5, y2       ) ;

        this.graphicsContext.moveTo( x1 + 0.5, y1 + 0.5 ) ; // Horizontal
        this.graphicsContext.lineTo( x2 + 0.5, y1 + 0.5 ) ;

        this.graphicsContext.stroke();
        this.graphicsContext.closePath() ;
    }
}

gameBoard.clearGameState = function()
{
    this.population = 0 ;
    this.generation = 0 ;

    // Fill cells with default values.
    for (let col = 0 ;  col < this.numCols ;  ++col)
    {
        for (let row = 0 ;  row < this.numRows ;  ++row)
        {
            let cell = this.cell[ row ][ col ] ;

            cell.numberOfNeighbors  =  0 ;
            cell.occupied           =  Occupancy.Empty ;
            cell.occupiedPreviously =  Occupancy.Indeterminate ;
            cell.state              =  State.Indeterminate ;
            cell.age                =  0 ;
            cell.label              = -1 ;
            cell.father             = -1 ;
            cell.edge               = -1 ;
        }
    }

    // Clear the comments.
    this.numCommentLines = 1 ;
    this.comment[ 0 ] = "#D Your comment here!" ;
}

// Redraw the gameboard and its global state.
gameBoard.updateView = function()
{
    for (let row = 0 ;  row < this.numRows ;  ++row)
    {
        for (let col = 0 ;  col < this.numCols ;  ++col)
        {
            let pos = [row, col] ;
            this.drawCell( pos ) ;
        }
    }

    let text = "Generation " + this.generation + " Population " + this.population ;

    // Display the game state.
    this.GameOfLifeState.innerHTML = text ;
}
