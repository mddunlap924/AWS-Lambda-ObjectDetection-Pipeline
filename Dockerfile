# AWS Lambda Docker Image
FROM amazon/aws-lambda-python:3.9.2021.08.23.12 as build

# Chrome drivers and Chrome-linux for Selenium to Work with AWS Lambda
RUN yum install -y unzip && \
    curl -Lo "/tmp/chromedriver.zip" "https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_linux64.zip" && \
    curl -Lo "/tmp/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F920005%2Fchrome-linux.zip?alt=media" && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/chrome-linux.zip -d /opt/

# Install dependencies
# https://aws.amazon.com/blogs/devops/serverless-ui-testing-using-selenium-aws-lambda-aws-fargate-and-aws-developer-tools/
# https://stackoverflow.com/questions/65429877/aws-lambda-container-running-selenium-with-headless-chrome-works-locally-but-not
FROM amazon/aws-lambda-python:3.9.2021.08.23.12
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y
RUN pip install selenium
COPY --from=build /opt/chrome-linux /opt/chrome
COPY --from=build /opt/chromedriver /opt/

# Copy over Python source code to be executed on AWS Lambda
COPY main.py ${LAMBDA_TASK_ROOT}
COPY awsplots ${LAMBDA_TASK_ROOT}/awsplots
COPY countobjects ${LAMBDA_TASK_ROOT}/countobjects
COPY yolov5 ${LAMBDA_TASK_ROOT}/yolov5
COPY yolov5n.pt ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Upgrade pip and install requirements.txt file
RUN pip install --upgrade pip
RUN pip install torch==1.10.0+cpu torchvision==0.11.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
RUN pip install -r requirements.txt

# Method Lambda will call in the main.py module
CMD ["main.handler"]
