
import numpy as np
import random
from .get_info import get_info
from datetime import datetime, timezone
import dateutil
import dateutil.parser
# Struct to represent each object


# Initialize the Q array with the sample input





class sort_model:



    def select_obj(self, messages):

        now = datetime.now(timezone.utc)
        # for message in messages:
            # timestamp = now - dateutil.parser.isoparse(message["created_at"]).total_seconds()
        return messages[:5]
















































    # # def __init__(self, queris):
    # #     len_q = len(queris)
    # #     for i, query in enumerate(queris):
    # #         Q[i] = object(query["t_time"], query["content_length"], query["id"])


    # # Q = [
    # #     Object(34, 21, 1232),
    # #     Object(42, 39, 1023),
    # #     Object(25, 13, 4443),
    # #     Object(11, 27, 8852),#
    # #     Object(17, 45, 1023),
    # #     Object(46, 31, 6245),
    # #     Object(8, 24, 6356),#
    # #     Object(12, 40, 9238),#
    # #     Object(19, 16, 9983),
    # #     Object(53, 22, 4532),
    # #     Object(14, 38, 1928),
    # #     Object(29, 27, 4857),
    # #     Object(41, 33, 9382),
    # #     Object(7, 19, 7894),#
    # #     Object(22, 15, 8837),
    # #     Object(49, 36, 2874),
    # #     Object(37, 43, 2980),
    # #     Object(15, 24, 8491),
    # #     Object(28, 18, 3451),
    # #     Object(10, 128, 1234)#
    # # ]
    # # print(Q)
    # # Sort the Q array by time (t) and length (l) to get TT and LL arrays
    # def select_obj(self, discord_channel_id):

        
    #     days_ago = 1


    #     cls_q = get_info()
    #     Q = cls_q.infomation(discord_channel_id, days_ago)


    #     # print(len(Q))

    #     # exit(0)
        
    #     TT = sorted(Q, key=lambda x: x.t)
    #     LL = sorted(Q, key=lambda x: -x.l)

    #     # Initialize the necessary parameters
    #     max_t = 0.0
    #     min_t = 0.0
    #     max_l = 0.0
    #     l_sum = 0.0
    #     ave_t = 0.0

    #     # Calculate max_t, min_t, and max_l
    #     max_t = sum(obj.t for obj in LL[:5]) / 5
    #     min_t = sum(obj.t for obj in TT[:5]) / 5
    #     max_l = max(obj.l for obj in Q)

    #     print("max_t =", max_t)
    #     print("min_t =", min_t)
    #     print("max_l =", max_l)

    #     # Initialize the dynamic programming array
    #     dp = np.zeros((6, 5))

    #     # Fill the dynamic programming array
    #     for i in range(6):
    #         for j in range(5):
    #             if i == 0 :
    #                 if j == 0:
    #                     dp[i][j] = 0.6 * Q[i].l / max_l + 0.4 * (1 - (Q[i].t - min_t) / (max_t - min_t))
    #             else:
    #                 if j > 0:
    #                     dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - 1] + 0.6 * Q[i].l / max_l + 0.4 * (1 - (Q[i].t - min_t) / (max_t - min_t)))
    #                 else:
    #                     dp[i][j] = max(dp[i - 1][j], 0.6 * Q[i].l / max_l + 0.4 * (1 - (Q[i].t - min_t) / (max_t - min_t)))

    #     try:
    #         # Reconstruct the selected objects
    #         Ans = [0] * 5
    #         real_ans = [0] * 5
    #         i, j = 5, 4
    #         print(i, j)
    #         while j >= 0 and i >= 0:
    #             if dp[i][j] != dp[i - 1][j]:
    #                 Ans[j] = i
    #                 real_ans[j] = Q[i].id
    #                 i -= 1
    #                 j -= 1
    #             else:
    #                 i -= 1
    #         l_sum = sum(Q[idx].l for idx in Ans) / 5
    #         ave_t = sum(Q[idx].t for idx in Ans) / 5
    #             # Calculate the function P
    #         P = 0.6 * l_sum / max_l + 0.4 * (1 - (ave_t - min_t) / (max_t - min_t))

    #         print("Ans = [", ", ".join(str(idx) for idx in Ans), "]")
    #         print("real_ans = [", ", ".join(str(idx) for idx in real_ans), "]")
    #         print("l_sum =", l_sum)
    #         print("ave_t =", ave_t)
    #         print("P =", P)
    #         print("max_t = ", max_t)
    #         print("min_t = ", min_t)
                

    #         return Ans   
    #     except Exception as e:
    #         print("An error occurred:", e)
