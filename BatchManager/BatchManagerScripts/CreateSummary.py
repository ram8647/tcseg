from xml.etree.ElementTree import ElementTree, parse
from itertools import product
from collections import OrderedDict
import ast
from ModelIOManager import IOManager
import fnmatch
import csv
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os.path

def create_summary(io_manager, type ='html'):
    '''
    write a file, either html or csv, that visually summarizes all the batch runs
    :type io_manager: IOManger
    '''

    def has_children(xml_element):
        return True if len(list(xml_element)) > 0 else False

    params_path = io_manager.params_path
    outpath = os.path.join(io_manager.output_folder, 'BatchSummary.html')

    if params_path.endswith('.txt'):
        with open(params_path, 'r') as in_file:
            with open(outpath, 'w') as out_file:
                in_file.write(out_file.read())

    elif params_path.endswith('.xml'):

        batch_vars_dict = OrderedDict()
        xml_file = parse(params_path)
        xml_root = xml_file.getroot()

        run_name = xml_root.attrib['name']

        for parameter_element in xml_root.iter('param'):
            if has_children(parameter_element):
                variable_name = parameter_element.attrib['name']
                print 'Including {}...'.format(variable_name)
                batch_vars_dict[variable_name] = []
                for values_element in parameter_element.iter('BatchValue'):
                    print '\twith value: {}...'.format(values_element.text)
                    new_batch_value = ast.literal_eval(values_element.text)
                    batch_vars_dict[variable_name].append(new_batch_value)

        all_combinations_of_params = product(*[batch_vars_dict[key] for key in batch_vars_dict])

        if type == 'csv' or type == '.csv':
            csv_outpath = outpath.replace('html','csv')
            with open(csv_outpath, 'wb') as csvfile:
                summary_writer = csv.writer(csvfile, delimiter=';')
                summary_writer.writerow(['run #']+batch_vars_dict.keys())

                for run_number, combo in enumerate(all_combinations_of_params):
                    combo_list = [str(element) for element in combo]
                    summary_writer.writerow([run_number]+combo_list)

        elif type == 'html' or type == '.html':
            with open(outpath, 'wb') as htmlfile:

                root = ET.Element('html')

                #Set up the meta-data
                head = ET.SubElement(root, 'head')
                site_title = ET.SubElement(head, 'title')
                site_title.text = str(run_name)
                css_stylesheet = ET.SubElement(head, 'link')
                css_stylesheet.set('rel','stylesheet')
                css_stylesheet.set('href', 'css/style.css')

                # Set up the page content
                body = ET.SubElement(root, 'body')
                main_div = ET.SubElement(body, 'div')
                main_div.set('align', 'center')

                title_div = ET.SubElement(main_div, 'div')
                title_div.set('class','table-title')
                title_div.set('align', 'center')
                title_h3 = ET.SubElement(title_div, 'h3')
                title_h3.text = 'Run Title: {}'.format(run_name)

                table = ET.SubElement(main_div, 'table')
                table.set('cellspacing', '0')
                table.set('id', 'summary')

                # Add the title row
                table_head = ET.SubElement(table, 'thead')
                title_row = ET.SubElement(table_head, 'tr')

                run_number_title_td = ET.SubElement(title_row, 'td')
                run_number_title_td.set('id','title')
                run_number_title_span = ET.SubElement(run_number_title_td, 'span')
                run_number_title_span.text = 'Run Number'

                for variable_name in batch_vars_dict:
                    batch_var_title_td = ET.SubElement(title_row, 'th')
                    batch_var_title_span = ET.SubElement(batch_var_title_td, 'span')
                    batch_var_title_span.text = variable_name

                video__title_td = ET.SubElement(title_row, 'td')
                video__title_td.set('id', 'title')
                video__title_span = ET.SubElement(video__title_td, 'span')
                video__title_span.text = 'Video (Click one!)'

                csv_title_td = ET.SubElement(title_row, 'td')
                csv_title_td.set('id', 'title')
                csv_title_span = ET.SubElement(csv_title_td, 'span')
                csv_title_span.text = 'CSV Output'

                # Add in the values by row
                table_body = ET.SubElement(table, 'tbody')
                for run_number, combo in enumerate(all_combinations_of_params):
                    row_td = ET.SubElement(table, 'tr')

                    # Add the run number
                    run_number_td = ET.SubElement(row_td, 'td')
                    run_number_td.text = str(run_number)

                    # Add the batch variables
                    combo_list = [str(element) for element in combo]
                    for element in combo_list:
                        element_td = ET.SubElement(row_td, 'td')
                        element_td.text = str(element)

                    # Add output'd files...
                    # ...including the final image and the movie
                    video_td = ET.SubElement(row_td, 'td')
                    open_video = ET.SubElement(video_td, 'a')
                    open_video.set('href', 'batch_run_{}.mov'.format(run_number))
                    img_element = ET.SubElement(open_video,'img')
                    img_element.set('src','tcseg_batch_{}_3600.png'.format(run_number))
                    img_element.set('height', '150')

                    # ...and the csv
                    csv_td = ET.SubElement(row_td, 'td')
                    open_csv = ET.SubElement(csv_td, 'a')
                    open_csv.set('href', 'batch_run_{}.csv'.format(run_number))
                    open_csv.text = 'batch_run_{}.csv'.format(run_number)

                # Finally, add in javascripts that make this dynamic
                scripts = ['http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js',
                           'http://tablesorter.com/__jquery.tablesorter.min.js',
                           'js/index.js']
                for script in scripts:
                    new_script = ET.SubElement(root, 'script')
                    new_script.set('src',script)
                    new_script.text = ' '

                rough_string = ET.tostring(root)
                reparsed = minidom.parseString(rough_string)
                pretty_str = reparsed.toprettyxml(indent="\t")
                pretty_str = pretty_str.replace('<?xml version="1.0" ?>','')

                htmlfile.write(pretty_str)

    else:
        print 'Unknown params file-type!'

