#!/bin/bash
mkdir -p curvfigs
for FILES in *.xtc
do
   NAME=`echo "$FILE" | cut -d'.' -f1`
   python3 lower-curvature.py $FILES input_file.gro
   python3 upper-curvature.py $FILES input_file.gro
   mv lower_curvature.png $NAME.png
   mv upper_curvature.png $NAME.png
   mv *png curvfigs
done

