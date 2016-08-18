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

    for i in range(4):
        default_growth_rate = 0.02
        if dict['r_mitosis_R{}'.format(i)] == [0.0] * 3:
            dict['r_grow_R{}'.format(i)] = [0.0] * 3
        else:
            if not 'r_grow_R{}'.format(i) in dict.keys():
                dict['r_grow_R{}'.format(i)] = [default_growth_rate] * 3

    error_check_params_dict(dict)
    return dict


def error_check_params_dict(dict):
    '''
    Make sure that all parameters are specified and raise an error if they are not
    '''
    necessary_variables = ['embryo_size', 'stripe_period', 'dye_flag', 'x0_dye', 'xf_dye', 'y0_dye', 'yf_dye',
                           'AP_growth_constraint_flag', 'forces_on', 'V_AP_GZposterior', 'k1_AP_GZanterior',
                           'k2_AP_GZanterior', 'k1_AP_Segments', 'k2_AP_Segments', 'k1_ML_GZ', 'k2_ML_GZ',
                           'k1_ML_Segments', 'k2_ML_Segments', 'mitosis_on', 'y_GZ_mitosis_border_percent',
                           'mitosis_transition_times', 'r_mitosis_R0', 'r_mitosis_R1', 'r_mitosis_R2', 'r_mitosis_R3',
                           'r_grow_R0', 'r_grow_R1', 'r_grow_R2', 'r_grow_R3', 'mitosis_fraction_AP_oriented',
                           'mitosis_window', 'mitosis_Vmin_divide', 'mitosis_Vmax', 'mitosis_visualization_flag',
                           'mitosis_visualization_window', 'dye_mitosis_clones', 'mitosis_dye_window']

    missing_variables = []
    for var in necessary_variables:
        if var not in dict:
            missing_variables.append(missing_variables)
    if len(missing_variables) > 0:
        raise NameError('Missing Variables! Please specify: {}',', '.join(missing_variables))
