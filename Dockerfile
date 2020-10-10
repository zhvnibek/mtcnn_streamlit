FROM python:3.8-slim-buster
#ENV APP_HOME /usr/getcontact_api
#WORKDIR /$APP_HOME
#COPY . $APP_HOME/
RUN pip3 install --no-cache-dir -r requirements.txt
CMD /bin/bash -c "streamlit run src/main.py"
EXPOSE 8501
