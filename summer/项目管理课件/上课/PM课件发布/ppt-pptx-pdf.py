import comtypes.client
import os
# 用ppt微软官方的接口转换最保险（关键免费），有些好用其它公司的包需要付费，非微软官方的包免费的也多多少少有些问题
def init_powerpoint():

    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
  
   
#   默认ppt就不会显示窗口，自己不要手残去设置为可见性参数为1
    return powerpoint

def ppt_to_pdf(powerpoint, inputFileName, outputFileName, formatType=32):
    if outputFileName[-3:] != 'pdf':
        outputFileName = outputFileName + ".pdf"
        # 是否显示窗口关键是 WithWindow=False参数，网上那些乱七八糟的方法都没用
    deck = powerpoint.Presentations.Open(inputFileName, WithWindow=False)
    deck.SaveAs(outputFileName, formatType)  # formatType = 32 for ppt to pdf
    deck.Close()

def convert_files_in_folder(powerpoint, folder):
    files = os.listdir(folder)
    pptfiles = [f for f in files if f.endswith((".ppt", ".pptx"))]
    for pptfile in pptfiles:
        fullpath = os.path.join(folder, pptfile)
        output_path = os.path.join(folder, "Output", os.path.splitext(pptfile)[0] + ".pdf")
        ppt_to_pdf(powerpoint, fullpath, output_path)

if __name__ == "__main__":
    print("Start")
    powerpoint = init_powerpoint()
    cwd = os.getcwd()
    output_folder = os.path.join(cwd, "Output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    convert_files_in_folder(powerpoint, cwd)
    powerpoint.Quit()
    print("Done")