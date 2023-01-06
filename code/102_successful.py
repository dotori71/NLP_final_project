import socket
import time
import json
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def DCRemover(x,w,alpha):
    w_n=x+alpha*w
    return [w_n,w_n-w]

class FindPT():
    def __init__(self):
        self.filter1 = [0.02879,0.03346,0.0488,0.06485,0.07991,
                        0.09225,0.10035,0.10317,0.10035,0.09225,
                        0.07991,0.06485,0.0488,0.03346,0.0288] 
        self.window1  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    def FindP(self,data1):
        self.window1 = [data1] + self.window1[0:14]
        self.rawData1 = self.window1[0]*self.filter1[0]+self.window1[1]*self.filter1[1]+self.window1[2]*self.filter1[2]+self.window1[3]*self.filter1[3]+self.window1[4]*self.filter1[4]+self.window1[5]*self.filter1[5]+self.window1[6]*self.filter1[6]+self.window1[7]*self.filter1[7]+self.window1[8]*self.filter1[8]+self.window1[9]*self.filter1[9]+self.window1[10]*self.filter1[10]+self.window1[11]*self.filter1[11]+self.window1[12]*self.filter1[12]+self.window1[13]*self.filter1[13]+self.window1[14]*self.filter1[14]


def calc_spo2(ir_data,red_data,ir_valley_locs, n_peaks):
    """
    By detecting  peaks of PPG cycle and corresponding AC/DC
    of red/infra-red signal, the an_ratio for the SPO2 is computed.
    """
    # find precise min near ir_valley_locs (???)
    exact_ir_valley_locs_count = n_peaks
    # find ir-red DC and ir-red AC for SPO2 calibration ratio
    # find AC/DC maximum of raw
    i_ratio_count = 0
    ratio = []
    # find max between two valley locations
    # and use ratio between AC component of Ir and Red DC component of Ir and Red for SpO2
    red_dc_max_index = -1
    ir_dc_max_index = -1
    for k in range(exact_ir_valley_locs_count-1):
        red_dc_max = -16777216
        ir_dc_max = -16777216
        if ir_valley_locs[k+1] - ir_valley_locs[k] > 3:
            for i in range(ir_valley_locs[k], ir_valley_locs[k+1]):
                if ir_data[i] > ir_dc_max:
                    ir_dc_max = ir_data[i]
                    ir_dc_max_index = i
                if red_data[i] > red_dc_max:
                    red_dc_max = red_data[i]
                    red_dc_max_index = i

            red_ac = int((red_data[ir_valley_locs[k+1]] - red_data[ir_valley_locs[k]]) * (red_dc_max_index - ir_valley_locs[k]))
            red_ac = red_data[ir_valley_locs[k]] + int(red_ac / (ir_valley_locs[k+1] - ir_valley_locs[k]))
            red_ac = red_data[red_dc_max_index] - red_ac  # subtract linear DC components from raw

            ir_ac = int((ir_data[ir_valley_locs[k+1]] - ir_data[ir_valley_locs[k]]) * (ir_dc_max_index - ir_valley_locs[k]))
            ir_ac = ir_data[ir_valley_locs[k]] + int(ir_ac / (ir_valley_locs[k+1] - ir_valley_locs[k]))
            ir_ac = ir_data[ir_dc_max_index] - ir_ac  # subtract linear DC components from raw

            nume = red_ac * ir_dc_max
            denom = ir_ac * red_dc_max
            if (denom > 0 and i_ratio_count < 5) and nume != 0:
                # original cpp implementation uses overflow intentionally.
                # but at 64-bit OS, Pyhthon 3.X uses 64-bit int and nume*100/denom does not trigger overflow
                # so using bit operation ( &0xffffffff ) is needed
                ratio.append(int(((nume * 100) & 0xffffffff) / denom))
                i_ratio_count += 1

    # choose median value since PPG signal may vary from beat to beat
    ratio = sorted(ratio)  # sort to ascending order
    mid_index = int(i_ratio_count / 2)

    ratio_ave = 0
    if mid_index > 1:
        ratio_ave = int((ratio[mid_index-1] + ratio[mid_index])/2)
    else:
        if len(ratio) != 0:
            ratio_ave = ratio[mid_index]

    if ratio_ave > 2 and ratio_ave < 184:
        spo2 = -45.060 * (ratio_ave**2) / 10000.0 + 30.054 * ratio_ave / 100.0 + 94.845
        spo2_valid = True
    else:
        spo2 = -999
        spo2_valid = False

    return spo2, spo2_valid


def decoding():
    global js,xdata1,ydata1,socketFlag,Datalist,mx,my,xdata,hrate,heart_rate,h_r_c,ydata2,SPO2,message
    message="waiting"
    xdata1 = []
    ydata1 = [] 
    ydata2=  []
    mx=[]
    my=[]
    irraw = [] 
    redraw=  []
    xdata=[]
    dca=[]   
    kk=0
    w=0
    w2=0  
    SPO2=0 
    xxx=[]
    heart_rate=[]
    h_r_c=0
    hrate=[]
    for i in range(200):
        xxx=xxx+[i]
    A=FindPT()
    B=FindPT()
    for i in range(0,200):
        ydata1 = ydata1 + [0]
        ydata2 = ydata2 + [0]
        xdata1 = xdata1 + [0] 
        xdata  = xdata  + [""]   
        irraw =  irraw  + [0] 
        redraw=  redraw + [0]
    while True:    
        if socketFlag==1:       
            if Datalist != [] and kk<len(Datalist) :
                if Datalist[kk][1]>120000:#判定手指有在上方
                    message="◡̈)successful detection"
                    irraw =  irraw[1:200] + [Datalist[kk][1]]
                    redraw=  redraw[1:200] + [Datalist[kk][0]]
                    mx=[]
                    my=[]
                    #remove dc value,remain ac value
                    dca=DCRemover(Datalist[kk][1],w,0.95)
                    iracvalue=dca[1]
                    w=dca[0]
                    A.FindP(iracvalue)
                    dca2=DCRemover(Datalist[kk][0],w2,0.95)
                    redacvalue=dca2[1]
                    w2=dca2[0]
                    B.FindP(redacvalue)  
                    ydata1 = ydata1[1:200] + [-A.rawData1]  # smoothed ir value serial and invert signal
                    ydata2 = ydata2[1:200] + [-B.rawData1]  # smoothed red value serial and invert signal
                    xdata1 = xdata1[1:200] + [Datalist[kk][2]] #time serial
                    list=[0,19,39,59,79,99,119,139,159,179,199]
                    for i in list:
                        xdata[i]=xdata1[i]       #x-axis ticks          
                    ir_grad = np.gradient(ydata1,xxx)
                    for k in range(199):
                        if ydata1[k]>10:    #threshold of peak detection 
                            if ir_grad[k]>=0 and ir_grad[k+1]<0: #peak location
                                mx.append(k) #put index of peaks in mx
                                my.append(ydata1[k])
                    hrate=[]
                
                    if len(mx)>=2:
                        for i in range(len(mx)-1): 
                            if (xdata1[mx[i+1]]-xdata1[mx[i]])!=0:
                                hrate.append(int(60/((xdata1[mx[i+1]]-xdata1[mx[i]])/1000)))         
                    heart_rate=heart_rate+hrate  
                    if len(heart_rate)>1 and len(heart_rate)%2000==0: #calculate an accurate hr per 2000 strokes
                        h_r_c=cal_hr(heart_rate)
                        heart_rate=[]      
                    SPO2, SPO2_valid=calc_spo2(irraw,redraw,mx,len(mx))
                    print("spo2:",SPO2)
                    kk=kk+1
                else:    
                    message="!!!wrong finger placement!!!"
                    kk=kk+1
            else:
                time.sleep(0.001)
        else:
            time.sleep(0.01)
            print('...等待連線...')
def cal_hr(heart_rate):
    n=1.5
    #IQR = Q3-Q1
    q3=np.percentile(heart_rate,75) 
    q1=np.percentile(heart_rate,25)
    IQR =q3-q1
    chr=[]
    for i in range(len(heart_rate)):
        if heart_rate[i]< q3+n*IQR and heart_rate[i]> q1-n*IQR:
            chr.append(heart_rate[i])
        #outlier1 = Q3 + n*IQR ; outlier2 = Q1 - n*IQR     
    hrc=np.mean(chr)
    return hrc

def draw():
    plt.style.use('ggplot')
    global ydata1,xdata1,mx,my,xdata,hrate,h_r_c,ydata2,SPO2,message
    fig1 = plt.figure(figsize=(9,9))
    fig1.patch.set_facecolor('pink')
    fig1.patch.set_alpha(0.6)
    ax=fig1.add_subplot(111)
    ax.patch.set_facecolor('mistyrose')
    ax.patch.set_alpha(1)
    x=np.linspace(0,200,200)
    y=np.linspace(-2000,2000,200)
    x1=[173.5,174.6]
    y1=[2014,2014]
    x3=[173.5,174.6]
    y3=[1905,1905]        
    line1,=ax.plot(x,y,"lightcoral",linewidth=3,label='Smoothed IR Data')
    l1,=ax.plot(x,y,"lightcoral",linewidth=4,label='Smoothed IR Data')
    line2,=ax.plot(x,y,"red",linewidth=3,label='Smoothed RED Data')
    l3,=ax.plot(x,y,"red",linewidth=4,label='Smoothed RED Data')    
    ax.set_title("Heart Rate & Pulse Oximeter",fontsize=17,\
        weight="bold",style="italic",color='darkred')
    ax.set_xlabel("Time(ms)",fontsize=10,color='darkred')
    ax.set_ylabel("Amplitude",fontsize=10,color='darkred')
    hr_t= ax.text(0.02, 0.93, '', transform=ax.transAxes,fontsize=11,color='maroon')
    hr= ax.text(0.1, 0.93, '', transform=ax.transAxes,fontsize=11,color='maroon')
    hr1= ax.text(0.02, 0.89, '', transform=ax.transAxes,fontsize=11,color='maroon')
    l1t= ax.text(0.84, 0.95, '', transform=ax.transAxes,fontsize=7)
    l2t= ax.text(0.84, 0.9, '', transform=ax.transAxes,fontsize=7)
    l2t2= ax.text(0.84,0.925, '', transform=ax.transAxes,fontsize=7) 
    sp3= ax.text(0.02, 0.85, '', transform=ax.transAxes,fontsize=11,color='mediumvioletred')
    sp4= ax.text(0.17, 0.85, '', transform=ax.transAxes,fontsize=11,color='mediumvioletred')    
    ms= ax.text(0.02, 0.81, '', transform=ax.transAxes,fontsize=11,color='rebeccapurple')   
    mdot,=ax.plot(x,y,label='Gradient Peaks',marker="$•$",mfc="darkorange",mec="sienna",markersize=10,linestyle='')      
    def update(data):
        global ydata1,xdata1,mx,my,xdata,hrate,h_r_c,ydata2,SPO2,message
        l2,=ax.plot(173.5,1772,label='Gradient Peaks',marker="$•$",mfc="darkorange",mec="sienna",markersize=10,linestyle='')         
        mdot.set_data(mx,my)
        line1.set_ydata(ydata1)
        line2.set_ydata(ydata2)
        plt.xticks(np.linspace(0,200,200),xdata)
        hr_t.set_text("HR set:")
        hr.set_text(hrate)
        hr1.set_text('HR: = %.1f BPM' % h_r_c)
        l1t.set_text('   Smoothed IR Data')
        l2t.set_text('   Gradient Peaks')
        l1.set_data(x1,y1)
        if SPO2!=-999:
            sp3.set_text('SPO2: = %.1f ' % SPO2)
            sp4.set_text('%')        
        l2t2.set_text('   Smoothed RED Data')
        l3.set_data(x3,y3)        
        ms.set_text(message)
        return 0
  
    '''set animation'''
    ani = animation.FuncAnimation(fig1, update, interval=50)
    plt.show()

def socket_client():
    global js,socketFlag,Datalist
    js=[list()]
    # IP
    Datalist=[]
    old_Datalist=0
    socketFlag=0
    HOST = '192.168.10.121'
    PORT = 2049
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print('Connect Success!')
    while True:
        str = "success"
        s.send(str.encode())
        socketFlag=1
        js=json.loads(s.recv(3072))
        if js != [] :
            Datalist=Datalist+js
        old_Datalist=Datalist
    s.close()
#
# if __name__=="__main__":
#     threading.Thread(target=socket_client,args=()).start()
#     threading.Thread(target=decoding,args=()).start()
#     threading.Thread(target=draw,args=()).start()

