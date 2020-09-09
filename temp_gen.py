# this file just generates a list of feasible experiments to run (BDP > 20)
# so we can manually distribute them amongst the clusters
MTU = 1502
allowed_exps = []
SIM_TIME_S = 605
cca = 0
edgeDel2=5
# 1000, 7000 on umass
for flows in reversed([1, 2]):
    for udp_bw_frac in [0.01]:
        # for flows in [200, 700]:
        for q_bdp in [2]:
            #     for q_bdp in [1/flows**0.5, 2, 6]:
            for bw in [5, 10, 20, 30, 40, 50]:
                for tbf in [False]:
                    for burst in [0]:
                    # for burst in [2, 5, 10, 20, 100]:
                        for paced in [True, False]:
                            for randSeed in range(1, 11, 1):
                                # fair_bdp_pkts = 7 * bw * 1024 * 1024 * 0.02 / 8 / flows / MTU
                                # if fair_bdp_pkts < 10:
                                #     continue
                                allowed_exps.append((flows, bw, edgeDel2, q_bdp))
                                print(
                                    rf'echo "cd ns-3-dev && ./waf --run-no-build \"paced_v_npaced --nodes={min(flows, 100)} --flows={flows} --simTime={SIM_TIME_S} --edgeDelay1=5 --edgeDelay2={edgeDel2} --btlSpeedMbps={bw} --edgeSpeedMbps={100} --bdpFactor={"%g" % q_bdp} --randSeed={randSeed}  --udpBwFrac={udp_bw_frac} --cca={cca} --paced={paced} --tbf={tbf} --burst={burst}\""')
print(len(allowed_exps))
pass
