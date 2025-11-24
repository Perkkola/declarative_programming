%
% Do NOT modify the following definition lines.
% The values for the constants below will be defined in an external data file.
%
% The number of cells
int: nofCells;
% The number of frequencies
int: nofFrequencies;

set of int: Cells = 1..nofCells;
set of int: Frequencies = 1..nofFrequencies;

% The separation matrix read from a data file
array[Cells,Cells] of int: separations;

% The matrix for illegal frequencies
array[Cells,Frequencies] of bool: illegal;

% Check data file consistency
constraint assert(forall(c in Cells)(separations[c,c] == 0), "separation matrix diagonal is not zero");
constraint assert(forall(c in Cells, d in Cells)(separations[c,d] == separations[d,c]), "separation matrix is not symmetric");
constraint assert(forall(c in Cells, d in Cells)(separations[c,d] >= 0), "separation matrix entries cannot be negative");

% Your constraints should force this array to be such that
% it fulfills the requirements given in the exercise description.
array[Cells] of var Frequencies: assignment;

% Insert your "constraint" statements here
constraint forall ([abs(assignment[i] - assignment[j]) >= separations[i, j] | i, j in 1..nofCells]);
constraint forall([illegal[i, assignment[i]] == false | i in 1..nofCells]);

solve satisfy;

% Do NOT modify the following line, it is used in the grading process
output ["assignment = \(assignment)\n"];
