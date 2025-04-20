import eel
import os


def Paralel_count(r1, r2):
    return r1 * r2 / (r1 + r2)

@eel.expose
def ResistanceCalc(v_out, v_ref, all_resistors):
    result = []
    counter = 0
    countersecond = 0
    counterthird = 0
    counterfourth = 0
    
    if v_out == v_ref:
        result.append("R1 = 0, R2 = NC (Не подключено)")
        return "\n".join(result)
    
    if v_ref > v_out:
        result.append("Ошибка: Vref не может быть больше Vout!")
        return "\n".join(result)

    counter = 0
    for r2 in all_resistors:
        r1 = r2 * (v_out / v_ref - 1)
        for res in all_resistors:
            if abs(res - r1) <= 0.0001:
                result.append(f'R1 = {res}, R2 = {r2}')
                counter += 1           
    
    if counter == 0:    #три резистора (--=два резистора паралельно=--резистор--)
        paralel_var = {}
        for r11 in all_resistors:
            for r12 in all_resistors:
                for r2 in all_resistors:
                    v_out_calc =  (v_ref) * ((r11 * r12) / ((r11 + r12) * r2) + 1)
                    key = abs(v_out - v_out_calc)
                    if paralel_var.get(key) != None:
                        paralel_var[key].append([r11, r12, r2])
                    else:
                        paralel_var.update({key: [[r11, r12, r2]]})    
        sorted_paralel_var = dict(sorted(paralel_var.items()))
        keys = list(sorted_paralel_var.keys())
        otv =[]
        for i in keys:
            if i <= 0.0001:
                otv.append(i)
                for pair in sorted_paralel_var[i]:
                    result_r = pair
                    ekv = round(Paralel_count(round(result_r[0], 6), round(result_r[1], 6)), 6)
                    result.append(f'R1.1 = {result_r[0]}, R1.2 = {result_r[1]} (Эквивалент R1 = {ekv}),\nR2 = {result_r[2]}')
                    countersecond += 1
    if countersecond == 0 and counter == 0:     #три резистора (--резистор--=два резистора паралельно=--)
        paralel_var = {}
        for r1 in all_resistors:
            for r21 in all_resistors:
                for r22 in all_resistors:
                    v_out_calc = v_ref * ((r1 * (r21 + r22)) / (r21 * r22) + 1)
                    key = abs(v_out - v_out_calc)
                    if paralel_var.get(key) != None:
                        paralel_var[key].append([r1, r21, r22])
                    else:
                        paralel_var.update({key: [[r1, r21, r22]]})
        sorted_paralel_var = dict(sorted(paralel_var.items()))
        keys = list(sorted_paralel_var.keys())
        otv =[]
        for i in keys:
            if i <= 0.00001:
                otv.append(i)
                for pair in sorted_paralel_var[i]:
                    result_r = pair
                    ekv = round(Paralel_count(round(result_r[1], 6), round(result_r[2], 6)), 6)
                    result.append(f'R1 = {result_r[0]},\nR2.1 = {result_r[1]}, R2.2 = {result_r[2]} (Эквивалент R2 = {ekv})')
                    counterthird += 1
    if countersecond == 0 and counter == 0 and counterthird == 0:   #четыре резистора (--два резистора паралельно--два резистора паралельно--)
        paralel_var = {}
        for r11 in all_resistors:
            for r12 in all_resistors:
                for r21 in all_resistors:
                    for r22 in all_resistors:
                        v_out_calc =  ((r11 / r21) * (r12 / r22)  * ((r21 + r22) / (r11 + r12)) + 1) * v_ref 
                        key = abs(v_out - v_out_calc)
                        if paralel_var.get(key) != None:
                            paralel_var[key].append([r11, r12, r21, r22])
                        else:
                            paralel_var.update({key: [[r11, r12, r21, r22]]})
        sorted_paralel_var = dict(sorted(paralel_var.items()))
        keys = list(sorted_paralel_var.keys())
        otv = []
        for i in keys:
            if i <= 0.00001:
                otv.append(i)
                for pair in sorted_paralel_var[i]:
                    result_r = pair
                    ekv = round(Paralel_count(round(result_r[0], 6), round(result_r[1], 6)), 6)
                    ekv2 = round(Paralel_count(round(result_r[2], 6), round(result_r[3], 6)), 6)
                    result.append(f'\nR1.1 = {result_r[0]}, R1.2 = {result_r[1]} (Эквивалент R1 = {ekv}),\nR2.1 = {result_r[2]}, R2.2 = {result_r[3]} (Эквивалент R2 = {ekv2})')
                    counterfourth += 1
    if countersecond == 0 and counter == 0 and counterthird == 0 and counterfourth == 0:
        result.append("Нет вариантов решения задачи")
    
    return "\n".join(result) if len(result) != 0 else "Нет вариантов решения."

eel.init(os.path.dirname(os.path.abspath(__file__)))
eel.start('main.html', size=(800, 800))