# flic-chatbot

python==3.9

conda activate flic-chatbot

cd user

streamlit run main.py

**EC2**

Setup môi trường ảo:

sudo yum install python3-pip -y

python3 -m venv venv

python3 -m pip install --upgrade pip

source venv/bin/activate

python3 -m pip install -r requirements.txt

**Cài đặt Ngrok**

wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip

unzip ngrok-stable-linux-amd64.zip

sudo mv ngrok /usr/local/bin

**Chạy server**

sudo yum update && sudo yum upgrade -y

cd /home/ec2-user/User

source venv/bin/activate

**Ngrok**

kill -9 `<Mã>`

ngrok http 8501 &

streamlit run main.py
