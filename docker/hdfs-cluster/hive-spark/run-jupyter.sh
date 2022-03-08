# start jupyter 
echo "==== Jupyter PATH env ===="
echo $PATH
echo "==== Jupyter starting... ===="
jupyter lab --allow-root --ip='*' --notebook-dir='/notebooks' --workspace='/notebooks' > /dev/null 2>&1 &
echo "==== Jupyter started. ===="
echo | jupyter server list  
