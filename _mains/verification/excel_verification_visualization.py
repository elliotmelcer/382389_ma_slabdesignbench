import os
from pathlib import Path

from matplotlib import pyplot as plt

plt.rcParams["font.family"] = "STIXGeneral"

from core.visualization_core.visualization import PlotLine, TU_COLORS, plot_moment_curvature_multiple, mirror_plot

# ─── Data ────────────────────────────────────────────────

m_kappa_c1_3_support = {
    "NONE_PARABOLIC": {
        "kappa": [0.00001, 0.000451, 0.000891, 0.001332, 0.001772, 0.002213, 0.002653, 0.003094, 0.003534, 0.003975, 0.004415, 0.004856, 0.005296, 0.005737, 0.006177, 0.006618, 0.007058, 0.007499, 0.007939, 0.00838, 0.008821, 0.009261, 0.009702, 0.010142, 0.010583, 0.011023, 0.011464, 0.011904, 0.012345, 0.012785, 0.013226, 0.013666, 0.014107, 0.014547, 0.014988, 0.015428, 0.015869, 0.016309, 0.01675, 0.017191, 0.022821],
        "moment": [0.1137, 5.1206, 10.1276, 15.1345, 20.1415, 25.1484, 30.1553, 35.1541, 40.1274, 45.0772, 50.0116, 54.9357, 59.8527, 64.7601, 69.6501, 74.5195, 79.3686, 84.2009, 89.0195, 93.8224, 98.6054, 103.3666, 108.1052, 112.8216, 117.5173, 122.1897, 126.8362, 131.4555, 136.0471, 140.6108, 145.144, 149.6436, 154.1077, 158.5353, 162.9258, 167.2767, 171.5821, 175.8382, 180.0432, 184.1957, 229.3571],
    },
    "TENSTIFF_PARABOLIC": {
        "kappa":  [0.00000000, 0.00001000, 0.00050600, 0.00057500, 0.00116100, 0.00174600, 0.00233200, 0.00291700, 0.00350200, 0.00461600, 0.00467300, 0.00525900, 0.00584400, 0.00643000, 0.00701500, 0.00760000, 0.00818600, 0.00877100, 0.00935700, 0.00994200, 0.01052700, 0.01111300, 0.01169800, 0.01228400, 0.01286900, 0.01345400, 0.01404000, 0.01462500, 0.01521100, 0.01579600, 0.01638200, 0.01696700, 0.01755200, 0.01813800, 0.01872300, 0.01930900, 0.01989400, 0.02047900, 0.02106500, 0.02165000, 0.02223600, 0.02282104],
        "moment": [0.0000, 0.8533, 43.2804, 47.6188, 57.3592, 57.3592, 57.3592, 57.3592, 57.3592, 57.3592, 57.8177, 63.1841, 68.9002, 74.8181, 80.8557, 86.9636, 93.1105, 99.2751, 105.4422, 111.6007, 117.7418, 123.8581, 129.9434, 135.9920, 141.9983, 147.9572, 153.8629, 159.7099, 165.4920, 171.2024, 176.8335, 182.3768, 187.8226, 193.1595, 198.3741, 203.4505, 208.3692, 213.1062, 217.6314, 221.9059, 225.8780, 229.4693],
    },
    "FCTM_PARABOLIC": {
        "kappa": [0.00000000, 0.00001000, 0.00050585, 0.00057541, 0.00116082, 0.00174623, 0.00233165, 0.00291706, 0.00379329, 0.00408788, 0.00467329, 0.00525870, 0.00584411, 0.00642952, 0.00701494, 0.00760035, 0.00818576, 0.00877117, 0.00935658, 0.00994199, 0.01052740, 0.01111281, 0.01169823, 0.01228364, 0.01286905, 0.01345446, 0.01403987, 0.01462528, 0.01521069, 0.01579610, 0.01638152, 0.01696693, 0.01755234, 0.01813775, 0.01872316, 0.01930857, 0.01989398, 0.02047940, 0.02106481, 0.02165022, 0.02223563, 0.02282104],
        "moment": [0.0000, 0.8533, 43.2804, 43.2804, 43.2804, 43.2804, 43.2804, 43.2804, 43.2804, 46.5659, 53.0929, 59.6074, 66.1036, 72.5775, 79.0262, 85.4473, 91.8387, 98.1981, 104.5234, 110.8124, 117.0627, 123.2716, 129.4364, 135.5541, 141.6212, 147.6341, 153.5885, 159.4797, 165.3026, 171.0510, 176.7181, 182.2960, 187.7755, 193.1457, 198.3939, 203.5047, 208.4595, 213.2352, 217.8029, 222.1252, 226.1530, 229.8187],
    },
    "ELASTIC_ELASTIC": {
        "kappa": [0.00000000, 0.00001000, 0.00051641, 0.00057541, 0.00116082, 0.00174623, 0.00233165, 0.00291706, 0.00350247, 0.00408788, 0.00467329, 0.00525870, 0.00584411, 0.00642952, 0.00701494, 0.00760035, 0.00818576, 0.00877117, 0.00935658, 0.00994199, 0.01052740, 0.01111281, 0.01169823, 0.01228364, 0.01286905, 0.01345446, 0.01403987, 0.01462528, 0.01521069, 0.01579610, 0.01638152, 0.01696693, 0.01755234, 0.01813775, 0.01872316, 0.01930857, 0.01989398, 0.02047940, 0.02106481, 0.02165022, 0.02223563, 0.02282104],
        "moment": [0.0000, 0.8381, 43.2804, 48.2254, 97.2889, 146.3525, 195.4160, 244.4795, 293.5430, 342.6066, 391.6701, 440.7336, 489.7971, 538.8607, 587.9242, 636.9877, 686.0512, 735.1148, 784.1783, 833.2418, 882.3053, 931.3689, 980.4324, 1029.4959, 1078.5594, 1127.6230, 1176.6865, 1225.7500, 1274.8135, 1323.8771, 1372.9406, 1422.0041, 1471.0676, 1520.1312, 1569.1947, 1618.2582, 1667.3217, 1716.3853, 1765.4488, 1814.5123, 1863.5758, 1912.6394]
    },
    "FACTOR_METHOD": {
        "kappa": [1.35663e-06, 6.10975e-05, 0.000120839, 0.00018058, 0.000240322, 0.000300063, 0.000359804, 0.000419448, 0.000478788, 0.002390698, 0.002985188, 0.003552392, 0.004098082, 0.004628346, 0.005144869, 0.005651769, 0.006149411, 0.006641065, 0.007126222, 0.007607482, 0.008084625, 0.00855731, 0.009027836, 0.009494789, 0.009960369, 0.010422971, 0.010884682, 0.01134382, 0.011802451, 0.012258834, 0.012714986, 0.013169097, 0.013623177, 0.014075396, 0.01452776, 0.0149784, 0.015429285, 0.015878523, 0.016328104, 0.016777106, 0.022463409],
        "moment": [0.1137, 5.1206, 10.1276, 15.1345, 20.1415, 25.1484, 30.1553, 35.1541, 40.1274, 45.0772, 50.0116, 54.9357, 59.8527, 64.7601, 69.6501, 74.5195, 79.3686, 84.2009, 89.0195, 93.8224, 98.6054, 103.3666, 108.1052, 112.8216, 117.5173, 122.1897, 126.8362, 131.4555, 136.0471, 140.6108, 145.1440, 149.6436, 154.1077, 158.5353, 162.9258, 167.2767, 171.5821, 175.8382, 180.0432, 184.1957, 229.3571],
    },
}


m_kappa_c1_3_midspan = {
    "NONE_PARABOLIC": {
        "kappa": [0.00001, 0.000387, 0.000764, 0.001141, 0.001518, 0.001895, 0.002272, 0.002649, 0.003026, 0.003403, 0.00378, 0.004157, 0.004534, 0.004911, 0.005288, 0.005665, 0.006042, 0.006419, 0.006796, 0.007173, 0.00755, 0.007927, 0.008304, 0.00868, 0.009057, 0.009434, 0.009811, 0.010188, 0.010565, 0.010942, 0.011319, 0.011696, 0.012073, 0.01245, 0.012827, 0.013204, 0.013581, 0.013958, 0.014335, 0.014712, 0.019431],
        "moment": [0.2152, 8.3273, 16.4394, 24.5515, 32.6637, 40.7758, 48.8879, 56.988, 65.0496, 73.0783, 81.086, 89.0796, 97.0633, 105.0336, 112.978, 120.891, 128.7748, 136.6354, 144.4772, 152.2971, 160.088, 167.846, 175.5697, 183.2616, 190.9249, 198.5552, 206.1477, 213.6998, 221.21, 228.6783, 236.1032, 243.4797, 250.8041, 258.074, 265.288, 272.4417, 279.5279, 286.5416, 293.479, 300.337, 374.3411],
    },
    "TENSTIFF_PARABOLIC": {
        "kappa": [0.00000000, 0.00001000, 0.00048849, 0.00051666, 0.00098698, 0.00148547, 0.00198396, 0.00248246, 0.00298095, 0.00347944, 0.00397793, 0.00447642, 0.00497491, 0.00547340, 0.00597189, 0.00647038, 0.00696888, 0.00746737, 0.00796586, 0.00846435, 0.00896284, 0.00946133, 0.00995982, 0.01045831, 0.01095680, 0.01145530, 0.01195379, 0.01245228, 0.01295077, 0.01344926, 0.01394775, 0.01444624, 0.01494473, 0.01544322, 0.01594171, 0.01644021, 0.01693870, 0.01743719, 0.01793568, 0.01843417, 0.01893266, 0.01943115],
        "moment": [0.0000, 0.8933, 43.8354, 46.3437, 63.2943, 69.8076, 73.8056, 77.6743, 81.0971, 85.2156, 92.6242, 101.3442, 110.6611, 120.3034, 130.1335, 140.0727, 150.0721, 160.0994, 170.1319, 180.1529, 190.1494, 200.1107, 210.0275, 219.8914, 229.6945, 239.4288, 249.0861, 258.6581, 268.1354, 277.5078, 286.7639, 295.8908, 304.8735, 313.6944, 322.3326, 330.7629, 338.9543, 346.8683, 354.4551, 361.6497, 368.3634, 374.4564],
    },
    "FCTM_PARABOLIC": {
        "kappa": [0.00000000, 0.00001000, 0.00048849, 0.00051666, 0.00098698, 0.00148547, 0.00211869, 0.00248246, 0.00298095, 0.00347944, 0.00397793, 0.00447642, 0.00497491, 0.00547340, 0.00597189, 0.00647038, 0.00696888, 0.00746737, 0.00796586, 0.00846435, 0.00896284, 0.00946133, 0.00995982, 0.01045831, 0.01095680, 0.01145530, 0.01195379, 0.01245228, 0.01295077, 0.01344926, 0.01394775, 0.01444624, 0.01494473, 0.01544322, 0.01594171, 0.01644021, 0.01693870, 0.01743719, 0.01793568, 0.01843417, 0.01893266, 0.01943115],
        "moment": [0.0000, 0.8933, 43.8354, 46.3437, 46.3437, 46.3437, 46.3437, 53.9452, 64.4672, 75.0175, 85.5652, 96.0952, 106.5992, 117.0715, 127.5081, 137.9055, 148.2604, 158.5698, 168.8305, 179.0393, 189.1926, 199.2867, 209.3175, 219.2805, 229.1707, 238.9825, 248.7097, 258.3453, 267.8815, 277.3090, 286.6175, 295.7949, 304.8270, 313.6973, 322.3856, 330.8679, 339.1146, 347.0884, 354.7421, 362.0134, 368.8183, 375.0385],
    },
    "ELASTIC_ELASTIC": {
        "kappa": [0.00000000, 0.00001000, 0.00048849, 0.00052727, 0.00098698, 0.00148547, 0.00198396, 0.00248246, 0.00298095, 0.00347944, 0.00397793, 0.00447642, 0.00497491, 0.00547340, 0.00597189, 0.00647038, 0.00696888, 0.00746737, 0.00796586, 0.00846435, 0.00896284, 0.00946133, 0.00995982, 0.01045831, 0.01095680, 0.01145530, 0.01195379, 0.01245228, 0.01295077, 0.01344926, 0.01394775, 0.01444624, 0.01494473, 0.01544322, 0.01594171, 0.01644021, 0.01693870, 0.01743719, 0.01793568, 0.01843417, 0.01893266, 0.01943115],
        "moment": [0.0000, 0.8789, 42.9354, 46.3437, 86.7496, 130.5639, 174.3782, 218.1925, 262.0068, 305.8211, 349.6354, 393.4497, 437.2640, 481.0783, 524.8925, 568.7068, 612.5211, 656.3354, 700.1497, 743.9640, 787.7783, 831.5926, 875.4069, 919.2212, 963.0354, 1006.8497, 1050.6640, 1094.4783, 1138.2926, 1182.1069, 1225.9212, 1269.7355, 1313.5498, 1357.3640, 1401.1783, 1444.9926, 1488.8069, 1532.6212, 1576.4355, 1620.2498, 1664.0641, 1707.8784]
    },
    "FACTOR_METHOD": {
        "kappa": [2.44841e-06, 9.47427e-05, 0.000187037, 0.000279331, 0.000371627, 0.000463921, 0.001501076, 0.001987468, 0.002445876, 0.002885904, 0.003313299, 0.003731588, 0.004143074, 0.004549282, 0.004951251, 0.005349806, 0.005745613, 0.006139193, 0.006530938, 0.006921123, 0.00730996, 0.007697631, 0.008084295, 0.008469127, 0.008854177, 0.009238562, 0.009622349, 0.010005603, 0.010388379, 0.01077073, 0.011152698, 0.011534313, 0.011915605, 0.012296603, 0.012677332, 0.013057812, 0.013438057, 0.013818082, 0.014197902, 0.014577532, 0.019314732],
        "moment": [0.2152, 8.3273, 16.4394, 24.5515, 32.6637, 40.7758, 48.8879, 56.9880, 65.0496, 73.0783, 81.0860, 89.0796, 97.0633, 105.0336, 112.9780, 120.8910, 128.7748, 136.6354, 144.4772, 152.2971, 160.0880, 167.8460, 175.5697, 183.2616, 190.9249, 198.5552, 206.1477, 213.6998, 221.2100, 228.6783, 236.1032, 243.4797, 250.8041, 258.0740, 265.2880, 272.4417, 279.5279, 286.5416, 293.4790, 300.3370, 374.3411],
    },
}

deflection_setup = {
    'x_positions': [0, 0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1375, 0.15, 0.1625,
                    0.175, 0.1875, 0.2, 0.2125, 0.225, 0.2375, 0.25, 0.2625, 0.275, 0.2875, 0.3, 0.3125, 0.325, 0.3375,
                    0.35, 0.3625, 0.375, 0.3875, 0.4, 0.4125, 0.425, 0.4375, 0.45, 0.4625, 0.475, 0.4875, 0.5
                    ],
    'M_qp': [0, 2.842993213, 5.614011914, 8.313056104, 10.94012578, 13.49522095, 15.9783416, 18.38948774, 20.72865938,
               22.99585649, 25.1910791, 27.3143272, 29.36560078, 31.34489985, 33.25222441, 35.08757446, 36.85095,
               38.54235103, 40.16177754, 41.70922954, 43.18470703, 44.58821001, 45.91973848, 47.17929243, 48.36687188,
               49.48247681, 50.52610723, 51.49776313, 52.39744453, 53.22515142, 53.98088379, 54.66464165, 55.276425,
               55.81623384, 56.28406816, 56.67992798, 57.00381328, 57.25572407, 57.43566035, 57.54362212, 57.57960938
             ],
    'M_rare': [0.0000, 3.7275, 7.3607,10.8995,14.3439,17.6940,20.9497,24.1110,27.1779,30.1505,33.0288,35.8126,38.5021,
               41.0972,43.5980,46.0043,48.3163,50.5340,52.6573,54.6862,56.6207,58.4609,60.2067,61.8581,63.4152,64.8779,
               66.2462,67.5202,68.6998,69.7850,70.7759,71.6724,72.4745,73.1823,73.7957,74.3147,74.7393,75.0696,75.3056,
               75.4471,75.4943
               ],
    'M_cr': [43.2804, 43.4317, 43.5791, 43.7227, 43.8624, 43.9984, 44.1305, 44.2588, 44.3832, 44.5038, 44.6206, 44.7336,
             44.8427, 44.9480, 45.0495, 45.1471, 45.2409, 45.3309, 45.4171, 45.4994, 45.5779, 45.6525, 45.7234, 45.7904,
             45.8536, 45.9129, 45.9684, 46.0201, 46.0680, 46.1120, 46.1522, 46.1886, 46.2212, 46.2499, 46.2748, 46.2958,
             46.3131, 46.3265, 46.3360, 46.3418, 46.3437
             ],
}
kappa_x = {
    'NONE_PARABOLIC': [0.0, 0.000241153, 0.00045953, 0.000657357, 0.000837296, 0.001001506, 0.001151391, 0.001288318, 0.001413413, 0.001528008, 0.001633087, 0.00172962, 0.001818293, 0.001899757, 0.001974633, 0.002043448, 0.002106683, 0.002164839, 0.002218316, 0.002267474, 0.002312638, 0.002354102, 0.002392218, 0.002427135, 0.002459064, 0.002488201, 0.002514724, 0.002538795, 0.002560557, 0.002580141, 0.002597661, 0.002613221, 0.002626911, 0.002638811, 0.00264899, 0.002657514, 0.002664461, 0.002669823, 0.002673632, 0.002675909, 0.002676667],
    'FCTM_PARABOLIC': [0.0, 0.000033162, 0.000065309, 0.000096480, 0.000126688, 0.000155941, 0.000184253, 0.000211632, 0.000238088, 0.000263632, 0.000288273, 0.000312020, 0.000334881, 0.000356866, 0.000377981, 0.000398235, 0.000417636, 0.000436190, 0.000453904, 0.000470786, 0.000486841, 0.000508981, 0.002173678, 0.002245844, 0.002308563, 0.002363114, 0.002410569, 0.002451832, 0.002487669, 0.002518730, 0.002545519, 0.002568457, 0.002587971, 0.002604425, 0.002618122, 0.002629313, 0.002638203, 0.002644955, 0.002649692, 0.002652500, 0.002653430],
    'TENSTIFF_PARABOLIC': [0.000000000, 0.000033177, 0.000065338, 0.000096523, 0.000126744, 0.000156011, 0.000184335, 0.000211726, 0.000238194, 0.000263750, 0.000288402, 0.000312159, 0.000335030, 0.000357024, 0.000378149, 0.000398412, 0.000417821, 0.000436383, 0.000454106, 0.000470995, 0.000487057, 0.000503681, 0.000519896, 0.000546268, 0.000582342, 0.000615266, 0.000645244, 0.000672457, 0.000697067, 0.000719221, 0.000739048, 0.000756662, 0.000772166, 0.000785648, 0.000797183, 0.000806836, 0.000814663, 0.000820705, 0.000824998, 0.000827564, 0.000828417],
    'ELASTIC_ELASTIC': [0.000000000, 0.000033843, 0.000066682, 0.000098526, 0.000129387, 0.000159275, 0.000188202, 0.000216177, 0.000243210, 0.000269310, 0.000294488, 0.000318751, 0.000342110, 0.000364572, 0.000386145, 0.000406837, 0.000426657, 0.000445611, 0.000463706, 0.000480950, 0.000497355, 0.000512968, 0.000527739, 0.000541663, 0.000554745, 0.000567004, 0.000578447, 0.000589077, 0.000598901, 0.000607921, 0.000616143, 0.000623570, 0.000630206, 0.000636053, 0.000641115, 0.000645394, 0.000648892, 0.000651611, 0.000653552, 0.000654716, 0.000655104],
    'Factor-Method': [0.0, 3.3877e-05, 6.6838e-05, 9.888e-05, 0.000130004, 0.000160207, 0.00018949, 0.00021785, 0.000245288, 0.000271803, 0.000297395, 0.000322063, 0.000345808, 0.00036863, 0.00039053, 0.001258033, 0.001372765, 0.001475571, 0.001568002, 0.001651325, 0.001726584, 0.001794654, 0.00185632, 0.001912166, 0.001962724, 0.002008458, 0.002049769, 0.002087003, 0.002120465, 0.002150418, 0.002177091, 0.002200683, 0.002221367, 0.002239293, 0.002254586, 0.002267359, 0.002277725, 0.002285716, 0.002291385, 0.002294772, 0.002295898],
}
EI_x = {
    'x_positions': [0, 0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1, 0.1125, 0.125, 0.1375, 0.15, 0.1625, 0.175, 0.1875, 0.2, 0.2125, 0.225, 0.2375, 0.25, 0.2625, 0.275, 0.2875, 0.3, 0.3125, 0.325, 0.3375, 0.35, 0.3625, 0.375, 0.3875, 0.4, 0.4125, 0.425, 0.4375, 0.45, 0.4625, 0.475, 0.4875, 0.5],
    'NONE_PARABOLIC': [11789, 11789, 12217, 12646, 13066, 13475, 13877, 14274, 14666, 15050, 15425, 15792, 16150, 16499, 16840, 17171, 17492, 17804, 18105, 18395, 18673, 18941, 19195, 19438, 19669, 19887, 20092, 20284, 20463, 20629, 20781, 20918, 21042, 21152, 21247, 21328, 21394, 21446, 21482, 21504, 21512],
    'FCTM_PARABOLIC': [85731, 85731, 85961, 86163, 86355, 86540, 86720, 86894, 87063, 87227, 87386, 87540, 87690, 87834, 87973, 88108, 88237, 88361, 88481, 88595, 88704, 87603, 21125, 21007, 20951, 20940, 20960, 21004, 21063, 21132, 21206, 21283, 21359, 21431, 21498, 21557, 21607, 21647, 21676, 21694, 21700],
    'TENSTIFF_PARABOLIC': [85693, 85693, 85922, 86125, 86317, 86502, 86681, 86855, 87024, 87188, 87347, 87501, 87651, 87795, 87934, 88069, 88198, 88322, 88441, 88556, 88665, 88525, 88325, 86367, 83056, 80424, 78305, 76582, 75168, 74004, 73041, 72244, 71586, 71045, 70604, 70250, 69972, 69764, 69619, 69534, 69506],
    'ELASTIC_ELASTIC': [84004, 84004, 84191, 84375, 84554, 84729, 84900, 85067, 85230, 85388, 85542, 85692, 85837, 85977, 86113, 86245, 86371, 86493, 86610, 86723, 86829, 86922, 87012, 87101, 87188, 87270, 87348, 87421, 87489, 87553, 87611, 87664, 87712, 87754, 87791, 87822, 87848, 87868, 87882, 87891, 87894],
    'Factor-Method': [83911, 83911, 83986, 84063, 84144, 84228, 84315, 84405, 84500, 84597, 84698, 84803, 84912, 85024, 85140, 27886, 26839, 26112, 25602, 25243, 24994, 24824, 24714, 24647, 24614, 24606, 24616, 24639, 24672, 24711, 24754, 24797, 24840, 24880, 24917, 24950, 24978, 25001, 25017, 25027, 25030],
}

deflection_mm = {
    'NONE_PARABOLIC': [13.66],
    'FCTM_PARABOLIC': [10.83],
    'TENSTIFF_PARABOLIC': [3.61],
    'ELASTIC_ELASTIC': [3.13],
    'Factor-Method': [10.44],
}

# Optional wrapper preserving the original table titles as string keys.
data = {
    "kappa(x)": kappa_x,
    "EI (x)": EI_x,
    "Deflection [mm]": deflection_mm,
}

# Helper Function
def dict_line_to_plot_line(
    data_dict: dict,
    line_key: str,
    *,
    name: str | None = None,
    color=None,
    linestyle: str = "solid",
) -> PlotLine:
    """
    Convert one y-series from a table-style dict into a PlotLine.

    x-values are taken from data_dict["x_positions"].
    y-values are taken from data_dict[line_key].
    """
    x_values = data_dict["x_positions"]
    y_values = data_dict[line_key]

    if len(x_values) != len(y_values):
        raise ValueError(
            f"Length mismatch for {line_key!r}: "
            f"{len(x_values)} x-values but {len(y_values)} y-values."
        )

    return PlotLine(
        x_values,
        y_values,
        name=name or line_key,
        color=color,
        linestyle=linestyle,
    )

# ── kappa(x) lines ────────────────────────────────────────────────────────────

kappa_line_none_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["NONE_PARABOLIC"],
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

kappa_line_fctm_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["FCTM_PARABOLIC"],
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

kappa_line_tenstiff_parabolic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["TENSTIFF_PARABOLIC"],
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

kappa_line_elastic_elastic = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["ELASTIC_ELASTIC"],
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

kappa_line_factor_method = PlotLine(
    deflection_setup["x_positions"],
    kappa_x["Factor-Method"],
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

kappa_lines = [
    kappa_line_none_parabolic,
    kappa_line_fctm_parabolic,
    kappa_line_tenstiff_parabolic,
    kappa_line_elastic_elastic,
    kappa_line_factor_method,
]

# ── EI(x) lines ───────────────────────────────────────────────────────────────

ei_line_none_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["NONE_PARABOLIC"],
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

ei_line_fctm_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["FCTM_PARABOLIC"],
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

ei_line_tenstiff_parabolic = PlotLine(
    EI_x["x_positions"],
    EI_x["TENSTIFF_PARABOLIC"],
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

ei_line_elastic_elastic = PlotLine(
    EI_x["x_positions"],
    EI_x["ELASTIC_ELASTIC"],
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

ei_line_factor_method = PlotLine(
    EI_x["x_positions"],
    EI_x["Factor-Method"],
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

ei_lines = [
    ei_line_none_parabolic,
    ei_line_fctm_parabolic,
    ei_line_tenstiff_parabolic,
    ei_line_elastic_elastic,
    ei_line_factor_method,
]

# Helper Function
def parabolic_deflection_values(x_positions: list[float], defl: float) -> list[float]:
    """
    Return parabolic deflection values for the given x-positions.
    """
    if not x_positions:
        return []

    x_0 = x_positions[0]
    x_end = x_positions[-1]

    if x_end == x_0:
        raise ValueError("x_positions must contain at least two different x-values.")

    L = x_end - x_0

    values = []
    for x in x_positions:
        t = (x - x_0) / L
        w = defl * (2 * t - t**2)
        values.append(w)

    return values

# ── Deflection lines ──────────────────────────────────────────────────────────

deflection_line_none_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["NONE_PARABOLIC"][0],
    ),
    name="NONE_PARABOLIC",
    color=TU_COLORS["BLUE"],
    linestyle="solid",
)

deflection_line_fctm_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["FCTM_PARABOLIC"][0],
    ),
    name="FCTM_PARABOLIC",
    color=TU_COLORS["GREEN"],
    linestyle="solid",
)

deflection_line_tenstiff_parabolic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["TENSTIFF_PARABOLIC"][0],
    ),
    name="TENSTIFF_PARABOLIC",
    color=TU_COLORS["RED"],
    linestyle="solid",
)

deflection_line_elastic_elastic = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["ELASTIC_ELASTIC"][0],
    ),
    name="ELASTIC_ELASTIC",
    color=TU_COLORS["VIOLET"],
    linestyle="solid",
)

deflection_line_factor_method = PlotLine(
    deflection_setup["x_positions"],
    parabolic_deflection_values(
        deflection_setup["x_positions"],
        deflection_mm["Factor-Method"][0],
    ),
    name="Factor-Method",
    color=TU_COLORS["ORANGE"],
    linestyle="solid",
)

deflection_lines = [
    deflection_line_none_parabolic,
    deflection_line_fctm_parabolic,
    deflection_line_tenstiff_parabolic,
    deflection_line_elastic_elastic,
    deflection_line_factor_method,
]

# ── Moment line ──────────────────────────────────────────────────────────

m_qp_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_qp"],
    name="M_qp",
    color=TU_COLORS["BLACK"],
    linestyle="solid",
)

m_rare_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_rare"],
    name="M_rare",
    color=TU_COLORS["BLACK"],
    linestyle="--",
)

m_cr_line = PlotLine(
    deflection_setup["x_positions"],
    deflection_setup["M_cr"],
    name="M_cr",
    color=TU_COLORS["BLACK"],
    linestyle="-.",
)

moment_lines = [
    m_qp_line,
    m_rare_line,
    m_cr_line,
]

# ── M-κ lines: support (x = 0) ────────────────────────────────────────────────

m_kappa_support_line_none_parabolic = PlotLine(m_kappa_c1_3_support["NONE_PARABOLIC"]["moment"], m_kappa_c1_3_support["NONE_PARABOLIC"]["kappa"], name="NONE_PARABOLIC", color=TU_COLORS["BLUE"], linestyle="solid")
m_kappa_support_line_fctm_parabolic = PlotLine(m_kappa_c1_3_support["FCTM_PARABOLIC"]["moment"], m_kappa_c1_3_support["FCTM_PARABOLIC"]["kappa"], name="FCTM_PARABOLIC", color=TU_COLORS["GREEN"], linestyle="solid")
m_kappa_support_line_tenstiff_parabolic = PlotLine(m_kappa_c1_3_support["TENSTIFF_PARABOLIC"]["moment"], m_kappa_c1_3_support["TENSTIFF_PARABOLIC"]["kappa"], name="TENSTIFF_PARABOLIC", color=TU_COLORS["RED"], linestyle="solid")
m_kappa_support_line_elastic_elastic = PlotLine(m_kappa_c1_3_support["ELASTIC_ELASTIC"]["moment"], m_kappa_c1_3_support["ELASTIC_ELASTIC"]["kappa"], name="ELASTIC_ELASTIC", color=TU_COLORS["VIOLET"], linestyle="solid")
m_kappa_support_line_factor_method = PlotLine(m_kappa_c1_3_support["FACTOR_METHOD"]["moment"], m_kappa_c1_3_support["FACTOR_METHOD"]["kappa"], name="Factor-Method", color=TU_COLORS["ORANGE"], linestyle="solid")

m_kappa_support_lines = [
    m_kappa_support_line_none_parabolic,
    m_kappa_support_line_fctm_parabolic,
    m_kappa_support_line_tenstiff_parabolic,
    m_kappa_support_line_elastic_elastic,
    m_kappa_support_line_factor_method,
]


# ── M-κ lines: midspan (x = 0.5) ──────────────────────────────────────────────

m_kappa_midspan_line_none_parabolic = PlotLine(m_kappa_c1_3_midspan["NONE_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["NONE_PARABOLIC"]["kappa"], name="NONE_PARABOLIC", color=TU_COLORS["BLUE"], linestyle="solid")
m_kappa_midspan_line_fctm_parabolic = PlotLine(m_kappa_c1_3_midspan["FCTM_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["FCTM_PARABOLIC"]["kappa"], name="FCTM_PARABOLIC", color=TU_COLORS["GREEN"], linestyle="solid")
m_kappa_midspan_line_tenstiff_parabolic = PlotLine(m_kappa_c1_3_midspan["TENSTIFF_PARABOLIC"]["moment"], m_kappa_c1_3_midspan["TENSTIFF_PARABOLIC"]["kappa"], name="TENSTIFF_PARABOLIC", color=TU_COLORS["RED"], linestyle="solid")
m_kappa_midspan_line_elastic_elastic = PlotLine(m_kappa_c1_3_midspan["ELASTIC_ELASTIC"]["moment"], m_kappa_c1_3_midspan["ELASTIC_ELASTIC"]["kappa"], name="ELASTIC_ELASTIC", color=TU_COLORS["VIOLET"], linestyle="solid")
m_kappa_midspan_line_factor_method = PlotLine(m_kappa_c1_3_midspan["FACTOR_METHOD"]["moment"], m_kappa_c1_3_midspan["FACTOR_METHOD"]["kappa"], name="Factor-Method", color=TU_COLORS["ORANGE"], linestyle="solid")

m_kappa_midspan_lines = [
    m_kappa_midspan_line_none_parabolic,
    m_kappa_midspan_line_fctm_parabolic,
    m_kappa_midspan_line_tenstiff_parabolic,
    m_kappa_midspan_line_elastic_elastic,
    m_kappa_midspan_line_factor_method,
]

" ── Plots ──────────────────────────────────────────────────────────"
# Moment, Stiffness, Curvature, Deflection
fig, axes = plt.subplots(
    nrows=4,
    ncols=1,
    figsize=(6, 9),
    constrained_layout=True,
)

ax1, ax2, ax3, ax4 = axes

mirror_plot(
    moment_lines,
    ax=ax1,
    xmarker=0.1,
    ymarker=10,
    flip_y_axis=True,
    title="Moments [kNm]",
    show_x_numbers=False,
    show_x_ticks=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 88),
)

mirror_plot(
    ei_lines,
    ax=ax2,
    xmarker=0.1,
    ymarker=25000,
    flip_y_axis=True,
    title="Stiffness EI [x10³ N/mm²]",
    show_x_numbers=False,
    show_x_ticks=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 110),
    y_scale=1e-3,
)

mirror_plot(
    kappa_lines,
    ax=ax3,
    xmarker=0.1,
    ymarker=0.5e-3,
    flip_y_axis=True,
    title="Curvatures [mm/m]",
    show_x_numbers=False,
    show_x_ticks=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 3.4),
    y_scale=1000,
)

mirror_plot(
    deflection_lines,
    ax=ax4,
    xmarker=0.1,
    ymarker=2.5,
    flip_y_axis=True,
    title="Deflection [mm]",
    show_x_numbers=False,
    show_x_ticks=False,
    show_legend=False,
    xlim=(0, 1.05),
    ylim=(0, 17),
)

handles = []
labels = []

for ax in [ax1, ax2, ax3, ax4]:
    ax_handles, ax_labels = ax.get_legend_handles_labels()

    for handle, label in zip(ax_handles, ax_labels):
        if label not in labels:
            handles.append(handle)
            labels.append(label)

fig.legend(
    handles,
    labels,
    loc="outside lower center",
    ncols=2,
    frameon=False,
)

fig.set_constrained_layout_pads(
    hspace=0.1,
    h_pad=0.05,
)

fig.subplots_adjust(bottom=20)

# M-K-Diagrams

fig_mk_support,      ax_support         = plot_moment_curvature_multiple(m_kappa_support_lines, title="C.1_3 with different constitutive laws", x=0.0, xlim = (0, 0.025), ylim = (0, 390), ymarker=50)
fig_mk_midspan,      ax_midspan         = plot_moment_curvature_multiple(m_kappa_midspan_lines, title="C.1_3 with different constitutive laws", x=0.5, xlim = (0, 0.025), ylim = (0, 390), ymarker=50)
fig_mk_support_zoom, ax_support_zoom    = plot_moment_curvature_multiple(m_kappa_support_lines, title="C.1_3 with different constitutive laws", x=0.0, xlim = (0, 0.005), ylim = (0, 100), ymarker=10)
fig_mk_midspan_zoom, ax_midspan_zoom    = plot_moment_curvature_multiple(m_kappa_midspan_lines, title="C.1_3 with different constitutive laws", x=0.5, xlim = (0, 0.005), ylim = (0, 100), ymarker=10)


# ── Save Figure  ──────────────────────────────────────────────────────────
FIGURES_DIR = Path(__file__).resolve().parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

fig.savefig(os.path.join(FIGURES_DIR,"excel_verification.pdf"), bbox_inches="tight")

fig_mk_support.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_support.pdf"), bbox_inches="tight")
fig_mk_midspan.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_midspan.pdf"), bbox_inches="tight")
fig_mk_support_zoom.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_support_zoom.pdf"), bbox_inches="tight")
fig_mk_midspan_zoom.savefig(os.path.join(FIGURES_DIR, "excel_c1_3_m_k_midspan_zoom.pdf"), bbox_inches="tight")

plt.show()