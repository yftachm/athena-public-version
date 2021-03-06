# Regression test based on MHD circularly polarized Alfven wave convergence problem
#
# Runs an isothermal cpaw convergence test in 2D including SMR and checks L1 errors (which
# are computed by the executable automatically and stored in the temporary file
# linearwave_errors.dat)

# Modules
import numpy as np
import math
import sys
import scripts.utils.athena as athena
import scripts.utils.comparison as comparison
sys.path.insert(0, '../../vis/python')

# Prepare Athena++
def prepare():
  athena.configure('b',
      prob='cpaw',
      eos='isothermal',
      flux='hlld')
  athena.make()

# Run Athena++
def run():
  # run R-going wave at two resolutions
  for i in (128,256):
    arguments = [
      'mesh/refinement=static',
      'mesh/nx1=' + repr(i), 'mesh/nx2=' + repr(i/2),
      'meshblock/nx1=' + repr(i/4), 'meshblock/nx2=' + repr(i/8),
      'output2/dt=-1', 'time/tlim=1.0', 'problem/compute_error=true']
    athena.run('mhd/athinput.cpaw2d', arguments)
  # run L-going wave
  arguments = [
    'mesh/refinement=static',
    'mesh/nx1=256', 'mesh/nx2=128',
    'meshblock/nx1=64', 'meshblock/nx2=32',
    'output2/dt=-1', 'time/tlim=1.0', 'problem/compute_error=true', 'problem/dir=2']
  athena.run('mhd/athinput.cpaw2d', arguments)

# Analyze outputs
def analyze():
  # read data from error file
  filename = 'bin/cpaw-errors.dat'
  data = []
  with open(filename, 'r') as f:
    raw_data = f.readlines()
    for line in raw_data:
      if line.split()[0][0] == '#':
        continue
      data.append([float(val) for val in line.split()])

  print data[0][4]
  print data[1][4]
  print data[2][4]

  # check absolute error and convergence
  if data[1][4] > 4.0e-8:
    print "error in L-going fast wave too large",data[1][4]
    return False
  if data[1][4]/data[0][4] > 0.3:
    print "not converging for L-going fast wave",data[0][4],data[1][4]
    return False

  # check error identical for waves in each direction
  if data[2][4] != data[0][4]:
    print "error in L/R-going Alfven waves not equal",data[2][4],data[0][4]
    return False

  return True
