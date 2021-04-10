#!/usr/bin/env python

import argparse
import sys,os


parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()


parser.add_argument('-f','--tunedFile', action='store',
        dest='tunedFile', required = True,
            help = "The job config file that will be used to configure the job (sort and init).")

parser.add_argument('-d','--dataFile', action='store',
        dest='dataFile', required = False, default = None,
            help = "The data/target file used to train the model.")

parser.add_argument('-r','--refFile', action='store',
        dest='refFile', required = False, default = None,
            help = "The reference file.")

parser.add_argument('-t', '--tag', action='store',
        dest='tag', required = True, default = None,
            help = "The tuning tag in the tuning branch in ringertunings repository")

parser.add_argument('-b', '--branch', action='store',
        dest='branch', required = True, default = None,
            help = "The tuning branch in ringetunings repository")

parser.add_argument('-v', '--volume', action='store',
        dest='volume', required = True, default = None,
            help = "The output path")

parser.add_argument('-p', '--proc', action='store',
        dest='proc', required = True, default = 'r0',
            help = "The process (usually tagged as r0, r1, ...).")



if len(sys.argv)==1:
  parser.print_help()
  sys.exit(1)

args = parser.parse_args()


def command(cmd):
  return True if os.system(cmd) == 0 else False

def check(path):
  return os.path.exists(path)


# we presume that this will be executed inside of the volume path given by the orchestra
if check(args.volume) and command("cd %s"%args.volume):


  if check('%s/ringer_tunings'%args.volume):
    command('rm -rf ringer')


  if check('%s/.complete'%args.volume):
    command('rm .complete')

  if check('%s/.failed'%args.volume):
    command('rm .failed')

  if check('%s/mylog.log'%args.volume):
    command('rm mylog.log')

  if not command("git clone https://github.com/ringer-atlas/ringer_tunings.git && cd ringer_tunings && git checkout %s && cd .."%(args.branch)):
    print("Its not possible to set the branch(%s) into the ringer repository"%args.branch)
    sys.exit(1)

  command("python ringer_tunings/versions/%s/%s/job_reprocess.py -d %s -v %s -f %s -r %s"%(args.tag, args.proc, args.dataFile, args.volume, args.tunedFile, args.refFile) )
  command('rm -rf ringer_tunings')

  sys.exit(0)
else:
  print('The volume (%s) path does not exist.', args.volume)
  sys.exit(1)









