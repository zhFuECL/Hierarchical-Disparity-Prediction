import os
import sys
import subprocess
from subprocess import CalledProcessError

## configuration ##
DATASETS = [ 
#    'fullsize'
#    'halfsize',
#    'Middlebury_1',
#    'Middlebury_4',
#    'Middlebury_others',
#    'Middlebury_bad',
]
ALGORITHMS = (
    'libelas',
#    'dp_mst_segment_only',
#    'dp_st_segment_only',
#    'dp_rt_segment_only',
#    'median_mst',
#    'median_st',
#    'median_rt',
#    'dp_mst_disp_in_edge_weight_uoi_30',
#    'dp_mst_disp_in_edge_weight_plus1',
#    'dp_mst_disp_in_edge_weight_abs_disp_diff_100',
#    'dp_mst',
#    'dp_st',
#    'dp_rt',
#    'mst',
#    'st',
#    'rt',
#    'dp_st_disp_prior',
)
CHECKER = 'checker_nonocc.bin'
use_lab = '0' # set to zero as default
####

## argument list ##
tolerance = sys.argv[1]
html_name_pre = sys.argv[2]
for dataset in sys.argv[3:] :
  DATASETS.append(dataset) # argv[1], argv[2], ... gives the dataset
####

dataset_table = {'halfsize': 0, 'fullsize': 1}

data_path = ''
pic_names = '' 
total = 0
correct = 0
table = {}
html_name = 'results/SuperReport_' + html_name_pre + '_err_ge_' + tolerance + '_'.join(DATASETS) + '.html'

def ratio(x) :
    return float(x[0]) / float(x[1])

def check_results(algo, path, dataset, picture) : #, left_result = 'leftdisp.pgm', right_result = 'rightdisp.pgm') :
    global correct
    global total
    para = 0
    with open(path + 'spec.txt','r') as f :
        para = f.read().split()
    output = ('results/' + picture + '_left_' + algo + '.pgm',
        'results/' + picture + '_left_' + algo + '.pgm')

    #run the algorithm
    print subprocess.check_output([
        'bin/main/' + algo + '.bin', 
        path + 'left.ppm', path + 'right.ppm', 
        para[0], para[1],
        output[0],
        str(dataset_table[dataset]),
        use_lab,
    ])

    command = ['bin/checker/'+CHECKER, output[0],
        path + 'displeft.pgm', path + 'dispright.pgm',
        tolerance, para[1]]

    res = subprocess.check_output(command)
    tmp = map(int, res.split())
    correct = correct + tmp[0]
    total = total + tmp[1]
    rati = float(tmp[0]) / tmp[1]
    print rati
    return 1-rati

for algorithm in ALGORITHMS :
    table[algorithm] = {}
    total = 0
    correct = 0
    temp0 = (correct, total)
    table[algorithm]['Overall'] = 0
    for dataset in DATASETS :
        table[algorithm][dataset] = {'Overall':0}
        pic_names = subprocess.check_output(['ls', 'testdata/' + dataset + '/']).split()
        temp = (correct, total)
        for picture in pic_names :
            print "~~~ "+ algorithm + '@' + dataset + '/' + picture +" ~~~"
            thepath = 'testdata/' + dataset + '/' + picture + '/'
            results = check_results(algorithm, thepath, dataset, picture)
            table[algorithm][dataset][picture] = results
            table[algorithm][dataset]['Overall'] += results
        table[algorithm][dataset]['Overall'] /= float(len(pic_names))
        table[algorithm]['Overall'] += table[algorithm][dataset]['Overall'] 
    table[algorithm]['Overall'] /= float(len(DATASETS))
print '\nDone.\n'

print "Saving result to " + html_name
report = open(html_name, 'w')
report.write('<!DOCTYPE html>\n<html>\n<body>\n')

report.write('<h1>Algorithm Overview</h1>\n')
report.write('<table border="3">\n')
report.write('<tr> <th>Algorithm</th> <th> ErrorRate </th> </tr>\n')
for algorithm in ALGORITHMS :
    report.write('<tr><td>'+algorithm+'</td>')
    report.write('<td> %.6f </td>' 
                % table[algorithm]['Overall'])
    report.write('</tr>\n')
report.write('</table>\n')

report.write('<h1>Dataset Overview</h1>\n')
report.write('<table border="3">\n')
report.write('<tr> <th>Algorithm</th> ')
for dataset in DATASETS :
    report.write('<th>'+dataset+'</th> ')
report.write('</tr>\n')
for algorithm in ALGORITHMS :
    report.write('<tr>')
    report.write('<td>' + algorithm + '</td>')
    for dataset in DATASETS :
        report.write('<td> %.6f </td>' 
            % table[algorithm][dataset]['Overall'])
    report.write('</tr>\n')
report.write('</table>\n')

report.write('<h1>Dataset Detail</h1>\n')
report.write('<table border="3">\n')
report.write('<tr><td>Test Data</td>')
for algorithm in ALGORITHMS :
    report.write('<td>'+algorithm+'</td>')
report.write('</tr>\n')

COLOR_RED =   "#F79F81"
COLOR_GREEN = "#BEF781"
for dataset in DATASETS :
    pic_names = subprocess.check_output(['ls', 'testdata/' + dataset + '/']).split()
    for picture in pic_names :
        report.write('<tr><td>'+dataset+'.'+picture+'</td>')
        tmp = [table[i][dataset][picture] for i in ALGORITHMS]

        for algorithm in ALGORITHMS :
            color = []
            if table[algorithm][dataset][picture] == min(tmp) :
                color = COLOR_RED
            elif table[algorithm][dataset][picture] == max(tmp) :
                color = COLOR_GREEN
            else :
                color = "white"
            report.write('<td bgcolor = ' + color + '>'+str(table[algorithm][dataset][picture])+'</td>')
        report.write('</tr>\n')

report.write('</html>')
report.close()
