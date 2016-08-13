def process_dictionary(dict):
    '''
    :param dict: the raw dictionary
    :return: a dictionary where all the values have been checked and manipulated if needed
    '''

    batch_interpreter_version = 'beta1'

    if 'r_mitosis_R123' in dict.keys():
        val = dict['r_mitosis_R123']
        dict['r_mitosis_R1'] = val
        dict['r_mitosis_R2'] = val
        dict['r_mitosis_R3'] = val
        del dict['r_mitosis_R123']

    if 'r_grow_R123' in dict.keys():
        val = dict['r_grow_R123']
        dict['r_grow_R1'] = val
        dict['r_grow_R2'] = val
        dict['r_grow_R3'] = val
        del dict['r_grow_R123']

    if 'r_mitosis_GZ' in dict.keys():
        val = dict['r_mitosis_GZ']
        dict['r_mitosis_R2'] = val
        dict['r_mitosis_R3'] = val
        del dict['r_mitosis_GZ']

    if 'r_grow_GZ' in dict.keys():
        val = dict['r_grow_GZ']
        dict['r_grow_R2'] = val
        dict['r_grow_R3'] = val
        del dict['r_grow_GZ']

    for i in range(3):
        default_growth_rate = 0.02
        if dict['r_mitosis_R{}'.format(i)] == [0.0] * 3
            dict['r_grow_R{}'.format(i)] = [0.0] * 3
        else:
            if not 'r_grow_R{}'.format(i) in dict:
                dict['r_grow_R{}'.format(i)] = [default_growth_rate] * 3


    return dict