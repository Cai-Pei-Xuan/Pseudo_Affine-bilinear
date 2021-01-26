from PIL import Image, ImageDraw
from sympy import symbols, solve

# 藉由8個點帶入函式(Pseudo affine)，並解出8個參數
def Equation(OriginalImage_Flatten_point, OriginalImage_point):

    a, b, c, d, e, f, g, h = symbols('a,b,c,d,e,f,g,h')
    x11, y11 = OriginalImage_Flatten_point[0]
    x12, y12 = OriginalImage_Flatten_point[1]
    x13, y13 = OriginalImage_Flatten_point[2]
    x14, y14 = OriginalImage_Flatten_point[3]

    x21, y21 = OriginalImage_point[0]
    x22, y22 = OriginalImage_point[1]
    x23, y23 = OriginalImage_point[2]
    x24, y24 = OriginalImage_point[3]
    
    f11 = a*x11*y11 + b*x11 + c*y11 + d - x21
    f12 = a*x12*y12 + b*x12 + c*y12 + d - x22
    f13 = a*x13*y13 + b*x13 + c*y13 + d - x23
    f14 = a*x14*y14 + b*x14 + c*y14 + d - x24

    sol1 = solve((f11, f12, f13, f14), a, b, c, d)
    
    f21 = e*x11*y11 + f*x11 + g*y11 + h - y21
    f22 = e*x12*y12 + f*x12 + g*y12 + h - y22
    f23 = e*x13*y13 + f*x13 + g*y13 + h - y23
    f24 = e*x14*y14 + f*x14 + g*y14 + h - y24
    
    sol2 = solve((f21, f22, f23, f24), e, f, g, h)
    
    return sol1[a], sol1[b], sol1[c], sol1[d], sol2[e], sol2[f], sol2[g], sol2[h]

# 將原圖中座標(x, y)做bilinear interpolation
def Bilinear(image, x, y):
    
    l = int(x)
    k = int(y)
    a = x - l
    b = y - k

    RGB_list = ['R', 'G', 'B']
    RGB_dict = {}
    for index, RGB in enumerate(RGB_list):
        RGB_dict[RGB] = int((1-a) * (1-b) * image.getpixel((l,k))[index] + a * (1-b) * image.getpixel((l+1,k))[index] + \
                        (1-a) * b * image.getpixel((l,k+1))[index] + a * b * image.getpixel((l+1,k+1))[index])

    return RGB_dict['R'], RGB_dict['G'], RGB_dict['B']

# 創建校正後的圖
def create_new_image(image_filename, output_filename):
  
    OriginalImage = Image.open(image_filename)
    width1, height1 = OriginalImage.size
    
    # 使用 https://www.ifreesite.com/image-coordinate/ 來取得圖的座標
    OriginalImage_Flatten_point = [(0, 0), (1278, 0), (0, 959), (1278, 959)]        # 物件校正後的4個座標(原圖的4個角落)
    OriginalImage_point = [(176, 132), (1116, 129), (27, 841), (1275, 826)]         # 原圖中物件的4個座標

    a, b, c, d, e, f, g, h = Equation(OriginalImage_Flatten_point, OriginalImage_point)   # 使用函式來解出a,b,c,d,e,f,g,h的參數

    newImage = Image.new(OriginalImage.mode, (width1, height1) , (255, 255, 255))   # 新建一個跟原圖一樣大小的圖
    width2, height2 = newImage.size
    draw = ImageDraw.Draw(newImage)                                           

    # 迴圈開始畫圖，從新圖的原點開始到最後一個點，逐步去做Pseudo affine+bilinear，並將新的像素填回新圖中
    for new_x in range(width2):                             
        for new_y in range(height2):
            x = (a * new_x * new_y) + (b * new_x) + (c * new_y) + d         # 經過Pseudo affine計算X
            y = (e * new_x * new_y) + (f * new_x) + (g * new_y) + h         # 經過Pseudo affine計算y
            
            R, G, B = Bilinear(OriginalImage, x, y)                         # 進行bilinear後將像素值填入圖中
            draw.point((new_x, new_y), fill = (R, G, B))
                   
    newImage.save(output_filename)       # 輸出圖片

if __name__ == '__main__':
    image_filename = 'Handout.jpg'                          # 原圖
    output_filename = 'output.jpg'                          # 新圖的檔名
    create_new_image(image_filename, output_filename)       # 創建新圖