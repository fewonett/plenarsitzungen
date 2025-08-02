import requests 

def get_links():
    list = []
    for i in range(1,21):
        for k in range(1,400):
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


def main():
    links = get_links()
    for link in links:
        filename = link[-9:]
        response = requests.get(link)
        # Save the PDF
        if response.status_code == 200:
            with open("pdfs/" + filename, "wb") as f:
                f.write(response.content)
        else:
            print(response.status_code)

if __name__ == "__main__":
    main()
