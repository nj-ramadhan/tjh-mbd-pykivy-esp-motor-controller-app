import  requests

f = open('coba.png', 'wb')
f.write(requests.get('https://api.sandbox.midtrans.com/v2/qris/24d83813-9217-4356-9380-9a8f7a7b57f6/qr-code').content)
f.close