'''Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve plot1.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/plot1
in your browser.
'''

import numpy as np
from os import listdir
from os.path import isfile, join
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HoverTool 
from bokeh.models.widgets import HBox, Slider,  VBoxForm, Select, RadioButtonGroup
from bokeh.io import curdoc
import itertools as it
from bokeh.models import PrintfTickFormatter

# Read CSV files
files = [f for f in sorted(listdir("./files")) if isfile(join("./files", f))]
source = ColumnDataSource(data=dict(x=np.array([0]), y=np.array([0]),size=np.array([0]),t1=['?'],t2=['?'],t3=['?'],t4=['?'],t5=['?'],t6=['?'],t7=['?'],t8=['?'],t9=['?'],t10=['?']))

# Set up plot
plot = Figure(plot_height=1000, plot_width=5000, title="Allocation Statistics",
              tools="crosshair,pan,reset,resize,save,wheel_zoom",
              x_range=[0,5000], y_range=[0, 1000],  y_axis_type="log",  title_text_font_size='18pt')
hover = HoverTool( tooltips=[ ("index", "$index"), ("(x,y)", "($x, $y)"), ("size","@size"),("t1", "@t1"),("t2", "@t2"),("t3", "@t3"),("t4", "@t4"),("t5", "@t5"),("t6", "@t6"),("t7", "@t7"),("t8", "@t8"),("t9", "@t9"),("t10", "@t10")] )
plot.add_tools(hover)
plot.xaxis.axis_label = "Time in ms"
plot.yaxis.axis_label = "Lifetime in ns"
plot.xaxis.major_label_text_font_size = "20pt"
plot.xaxis.axis_label_text_font_size = "25pt"
plot.yaxis.major_label_text_font_size = "20pt"
plot.yaxis.axis_label_text_font_size = "25pt"
plot.xaxis[0].formatter = PrintfTickFormatter(format="%16.3f")
plot.scatter('x', 'y', source=source, size=3, color="#3A5785", alpha=1)

# Select File
filename = Select(title="\nChoose File: \n", value="File", options=["Files"]+files)

# Select Subset
subsets = []
time = Select(title="\nChoose Subset: \n", value="Subset", options=["Subset"]+subsets)


# Generate dictionary for stackIds
stackIds = {}
for i in open("mallocHook.115665.fom_sourcelines"):
   tmp = i.split()
   stackId = int(tmp.pop(0)) 
   stackIds[stackId] = tmp

data  = np.array([])
stack = np.array([])
def update_data1(attrname, old, new):
    if filename.value != "File":
      global data
      global stack
      print "Reading the file ..."
      time.value = "Subset"
      time.options = ["Subset"]
      time.update()
      try:
        data  = np.loadtxt("./files/"+str(filename.value))
      except:
        with open("./files/"+str(filename.value)) as f:
          data = np.array(list(it.izip_longest(*[line.split() for line in f], fillvalue=-1)), dtype=np.int).T
      print "Finished reading ..."
      timerange = data.shape[0]/5000
      time.value = "Subset"
      time.update()
      subsets = ["Subset"]
      for i in range(0,timerange+1):
        subsets.append(str(i))
      time.options= subsets
      time.update() 

tooltip = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]}

def update_data3(attrname, old, new):
    global data
    global stackIds
    global stack
    global tooltip
    if time.value != "Subset":
      t1 = int(time.value) * 5000
      t2 = t1 + 5000

      # Generate new data
      x = (data[t1:t2,0] - 3813512231007647)/1000000.0
      y = data[t1:t2,3]
      s = data[t1:t2,2]
     
      plot.x_range.start = x[0]
      plot.x_range.end   = x[-1]
      plot.y_range.start = np.min(y)
      plot.y_range.end   = np.max(y)
      source.data = dict(x=x, y=y)
      
      stack = data[t1:t2,4:14]     
      print "Generating stacktraces..."
      tooltip = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[],"9":[],"10":[]}
      for i in range(0,stack.shape[0]):
        c = 0
        for id in stack[i]:
          c = c + 1
          try:
            line = stackIds[id][-2].split("/")[-1][0:-1]
          except:
            line = " "
          try:
            func = stackIds[id][1:-4]
            func = ' '.join(func)
            func = func.split("+")[0][:150]
          except:
            func = " "

          tooltip[str(c)].append(line + " : " + func)
      source.data = dict(x=x, y=y, size=s, t1=tooltip["1"], t2=tooltip["2"], t3=tooltip["3"], t4=tooltip["4"],t5=tooltip["5"],t6=tooltip["6"],t7=tooltip["7"],t8=tooltip["8"],t9=tooltip["9"],t10=tooltip["10"])
      print "Finished generating stacktraces..."      

filename.on_change('value', update_data1)
time.on_change('value', update_data3)
inputs = VBoxForm(children=[filename, time])

curdoc().add_root(HBox(children=[inputs, plot], width=5250))
