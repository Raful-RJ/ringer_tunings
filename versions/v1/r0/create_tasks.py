import os
basepath = os.getcwd()

path = basepath + '/Zrad/v1/r0'


command = """maestro.py task create \
  -v {PATH} \
  -t user.jodafons.mc16_13TeV.sgn.medium.gammajet.bkg.vetoloose.dijet.v1_et{ET}_eta{ETA}.r0 \
  -c user.jodafons.job_config.Zrad_v1.n2to5.10sorts.5inits.r0 \
  -d user.jodafons.mc16_13TeV.sgn.medium.gammajet.bkg.vetoloose.dijet_et{ET}_eta{ETA}.npz \
  --sd "{REF}" \
  --exec "run_tuning.py -c %IN -d %DATA -r %REF -v %OUT -b zrad -t v1 -p r0" \
  --queue "gpu" """

try:
    os.makedirs(path)
except:
    pass

for et in range(5):
    for eta in range(5):
        ref = "{'%%REF':'user.jodafons.mc16_13TeV.sgn.medium.gammajet.bkg.vetoloose.dijet_et%d_eta%d.ref.pic.gz'}"%(et,eta)
        cmd = command.format(ET=et,ETA=eta,REF=ref,PATH=path)
        print(cmd)
        os.system(cmd)
