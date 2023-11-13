import requests

# try :
#     r = requests.get('https://app.kickyourplast.com/api/products', {all : True})
#     print(r.json()['data'][0])
# except Exception as e:
#     print(e)

try :
    r = requests.post('https://app.kickyourplast.com/api/machine_transactions', json={
        "payment_method": "gopay",
        "machine_code": "001",
        "phone": "082138685500",
        "items": [
            {
                "product_id": 2,
                "qty": 2,
                "size": 600,
                "unit_price": 3500,
                "drink_type": "cold"
            }
        ]
    })
    print(r.json()['data'])
except Exception as e:
    print(e)

