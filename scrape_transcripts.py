import requests 

def get_links():
    list = []
    for i in range(1,21):
        for k in range(1,281):
            a = str(i)
            if len(a) < 2:
                a = '0'+ a
            b = str(k)
            while len(b) < 3:
                b = '0' + b
            b = a + b
            numb =  a + '/' + b
            list.append('https://dserver.bundestag.de/btp/'+ numb + '.pdf')

    return(list)


          # " https://dserver.bundestag.de/btp/01/01001.pdf"




links = get_links()
    
filename = 'test.pdf'

url = 'https://dserver.bundestag.de/btp/01/01001.pdf'
response = requests.get(url)
# Save the PDF
if response.status_code == 200:
    with open(filename, "wb") as f:
        f.write(response.content)
else:
    print(response.status_code)
        

main()

