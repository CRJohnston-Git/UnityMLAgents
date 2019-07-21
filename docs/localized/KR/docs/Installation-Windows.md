# Windows ����ڸ� ���� ML-Agents Toolkit ��ġ ���

ML-Agents toolkit�� Windows 10�� �����մϴ�. �ٸ� ������ Windows�� ����� ���� ML-Agents toolkit�� 
����� ���� ������ �������� �ʾҽ��ϴ�. ������, ML-Agents toolkit�� Bootcamp �Ǵ� ���� ó�� ȯ�� ���� 
Windows VM�� ��� ���� �������� �ʾҽ��ϴ� .

ML-Agents toolkit�� ����ϱ� ����, �Ʒ��� ����Ȱ� ó�� Python�� �䱸�Ǵ� Python ��Ű���� ��ġ�ؾ� �մϴ�.
�� ���̵�� ���� GPU ��� �н�(�����ڸ� ����)�� ���� ���� ����� �ٷ�ϴ�. ���� ML-Agents toolkit�� ���� GPU ��� �н���
�ʿ����� ������ ���� ���� �Ǵ� Ư�� ���׿� �ʿ��� �� �ֽ��ϴ�.

## �ܰ� 1: Anaconda�� ���� Python ��ġ

Windows ������ Anaconda�� [�ٿ�ε�](https://www.anaconda.com/download/#windows)�ϰ� ��ġ�Ͻʽÿ�.
Anaconda�� ��������ν�, �ٸ� ���� ������ Python�� �и��� ȯ�濡�� ������ �� �ֽ��ϴ�.
Python 2�� ���̻� �������� �ʱ� ������ Python 3.5 �Ǵ� 3.6�� �ʿ��մϴ�. �� ���̵忡�� �츮�� 
Python 3.6 ������ Anaconda 5.1 ������ ����� ���Դϴ�.
([64-bit](https://repo.continuum.io/archive/Anaconda3-5.1.0-Windows-x86_64.exe)
�Ǵ� [32-bit](https://repo.continuum.io/archive/Anaconda3-5.1.0-Windows-x86.exe)
��ũ).

<p align="center">
  <img src="images/anaconda_install.PNG"
       alt="Anaconda Install"
       width="500" border="10" />
</p>

����Ʈ _advanced installation options_�� �����ϴ� ���� ��õ������ ��Ȳ�� ���� ������ �ɼ��� �����Ͻʽÿ�.

<p align="center">
  <img src="images/anaconda_default.PNG" alt="Anaconda Install" width="500" border="10" />
</p>

��ġ �Ŀ� �ݵ�� __Anaconda Navigator__�� ���� ������ �Ϸ��ؾ� �մϴ�.
Windows Ž�� â����, _anaconda navigator_.�� Ÿ�����Ͽ� Anaconda Navigator �� �� �� �ֽ��ϴ�.

ȯ�� ������ �����Ǿ����� �ʴٸ� `conda`��� � ��ɾ� ���ο� Ÿ�������� ��
"conda is not recognized as internal or external command" ��� ������ ���� ���Դϴ�.
�̸� �ذ��ϱ� ���� ��Ȯ�� ȯ�� ���� ������ �ʿ��մϴ�.

Ž�� â���� `ȯ�� ����`�� Ÿ���� �Ͽ� (������ Ű�� �����ų� ���� �Ʒ� ������ ��ư�� ���� �� �� �ֽ��Ͻ��ϴ�). 
 __�ý��� ȯ�� ���� ����__ �ɼ��� �ҷ��ɴϴ�.

<p align="center">
  <img src="images/edit_env_var_kr.png"
       alt="edit env variables"
       width="250" border="10" />
</p>

�� �ɼǿ��� __ȯ�� ����__ ��ư�� Ŭ���ϰ�. �Ʒ�  under
__�ý��� ����__���� "Path" ������ ���� Ŭ���ϰ� __���� �����__�� Ŭ���Ͽ� ���� �� path�� �߰��Ͻʽÿ�.

```console
%UserProfile%\Anaconda3\Scripts
%UserProfile%\Anaconda3\Scripts\conda.exe
%UserProfile%\Anaconda3
%UserProfile%\Anaconda3\python.exe
```

## �ܰ� 2: ���ο� Conda ȯ�� ���� �� Ȱ��ȭ

ML-Agents toolkit�� �Բ� ����� ���ο� [Conda ȯ��](https://conda.io/docs/)�� ���� ���Դϴ�.
�� �۾��� ��ġ�� ��� ��Ű���� �� ȯ�濡�� ���ѵȴٴ� ���� �ǹ��մϴ�. �̴� �ٸ� ȯ���̳� �ٸ� ���̽� ��ġ��
������ ��ġ�� �ʽ��ϴ�. ML-Agents�� ������ ������ �׻� Conda ȯ���� Ȱ��ȭ ���Ѿ� �մϴ�.

���ο� Conda ȯ���� ����� ����, ���ο� Anaconda ������Ʈ(Ž�� â���� _Anaconda Prompt_�� Ŭ��)�� ���� ����
��ɾ Ÿ���� �Ͻʽÿ�:

```sh
conda create -n ml-agents python=3.6
```

�� ��Ű���� ��ġ�ϱ� ���� �޼����� ���� ��� `y`�� Ÿ�����ϰ� ���͸� �����ʽÿ� _(���ͳ��� ����Ǿ��ִ��� Ȯ���Ͻʽÿ�)_.
�� �䱸�Ǵ� ��Ű������ �ݵ�� ��ġ�ؾ� �մϴ�. ���ο� Conda ȯ�濡�� Python 3.6 ������ ���Ǹ� ml-agents�� ȣ��˴ϴ�.

<p align="center">
  <img src="images/conda_new.PNG" alt="Anaconda Install" width="500" border="10" />
</p>

�ռ� ���� ȯ���� �̿��ϱ� ���� �ݵ�� Ȱ��ȭ�� �ؾ��մϴ�. _(���Ŀ� ���� ��ɾ� ���� ȯ���� ������ �� �ֽ��ϴ�)_.
���� Anaconda ������Ʈ���� ���� ��ɾ Ÿ���� �Ͻʽÿ�:

```sh
activate ml-agents
```

Ȱ��ȭ �Ŀ� `(ml-agents)`��� ���ڰ� ������ �� �տ� ��Ÿ���� ���� �� �� �ֽ��ϴ�.

��������, `tensorflow`�� ��ġ�մϴ�. ���̽� ��Ű���� ��ġ�ϱ� ���� ����ϴ� `pip`��� ��Ű�� ���� �ý��۸� ����Ͽ� ��ġ�� �� �ֽ��ϴ�.
�ֽ� ������ TensorFlow�� �۵����� ���� �� �����Ƿ�, ��ġ ������ 1.7.1���� Ȯ���ؾ� �մϴ�. ���� Anaconda ������Ʈ â����
���� ��ɾ Ÿ���� �Ͻʽÿ�._(���ͳ��� ����Ǿ� �ִ��� Ȯ���Ͽ� �ֽʽÿ�)_:

```sh
pip install tensorflow==1.7.1
```

## �ܰ� 3: �ʼ� ���̽� ��Ű�� ��ġ

ML-Agents toolkit�� ���� ���̽� ��Ű���� �������Դϴ�. `pip`�� ����Ͽ� �� ���̽� ���Ӽ����� ��ġ�Ͻʽÿ�. 

ML-Agents Toolkit ����� ����Ұ� ���� ��ǻ�Ϳ� �����Ǿ����� �ʾҴٸ� �����Ͻʽÿ�. Git�� ([�ٿ�ε�](https://git-scm.com/download/win))�ϰ�
�����Ų �� ���� ��ɾ Anaconda ������Ʈâ�� �Է��Ͽ� ������ �� �ֽ��ϴ�. _(���� �� ������Ʈ â�� �����ִٸ� `activate ml-agents`�� Ÿ�����Ͽ�
ml-agents Conda ȯ���� Ȱ��ȭ �Ǿ��ִ��� Ȯ���Ͻʽÿ�)_:

```sh
git clone https://github.com/Unity-Technologies/ml-agents.git
```

���� Git�� ����ϰ� ���� �ʴٸ� ������ [��ũ](https://github.com/Unity-Technologies/ml-agents/archive/master.zip)���� ��� ������ �ٿ�ε� �� �� �ֽ��ϴ�.

`UnitySDK` ���� ���丮���� ������Ʈ�� �߰��� ����Ƽ �ּ��� ���ԵǾ� �ֽ��ϴ�. ���� �����ϴµ� ������ �Ǵ� ���� [���� ȯ��](Learning-Environment-Examples.md)���� �ֽ��ϴ�.

`ml-agents` ���� ���丮���� ����Ƽ ȯ��� �԰� ����ϴ� ���� ��ȭ�н� Ʈ���̳� ���̽� ��Ű���� ���ԵǾ� �ֽ��ϴ�.

`ml-agents-envs` ���� ���丮���� `ml-agents` ��Ű���� ���ӵǴ� ����Ƽ�� �������̽��� ���� ���̽� API�� ���ԵǾ� �ֽ��ϴ�. 

`gym-unity` ���� ���丮���� OpenAI Gym�� �������̽��� ���� ��Ű���� ���ԵǾ� �ֽ��ϴ�.

`mlagents-learn`�� ������ �� Ʈ���̳��� ȯ�� ���� ������ �� ���丮 �ȿ� �ʿ��ϹǷ�, ������ �ٿ�ε� �� ���丮�� ��ġ�� ����Ͻʽÿ�.
���ͳ��� ����Ǿ����� Ȯ���ϰ� Anaconda ������Ʈ���� ���� ��ɾ Ÿ���� �Ͻʽÿ�t:

```console
pip install mlagents
```

ML-Agents toolkit�� ������ �� �ʿ��� ��� ���̽� ��Ű���� ��ġ�� �Ϸ��� ���Դϴ�.

Windows���� ���� pip�� ����Ͽ� Ư�� ���̽� ��Ű���� ��ġ�� �� ��Ű���� ĳ���� �д� ���� ���� ���� �ֽ��ϴ�.
������ ���� ������ �ذ��� �� �� �ֽ��ϴ�:

```console
pip install mlagents --no-cache-dir
```

`--no-cache-dir`�� pip���� ĳ���� ��Ȱ��ȭ �Ѵٴ� ���Դϴ�.

### ������ ���� ��ġ 

���� `ml-agents` �Ǵ� `ml-agents-envs`�� �����ϰ� �ʹٸ�, PyPi�� �ƴ� ������ ����ҷ� ���� ��Ű���� ��ġ�ؾ� �մϴ�.
�̸� ����, `ml-agents` �� `ml-agents-envs` �� ���� ��ġ�ؾ� �մϴ�. 
 
�������� ������ `C:\Downloads`�� ��ġ�� �ֽ��ϴ�. ������ �����ϰų� �ٿ�ε��� �� 
Anaconda ������Ʈ���� ml-agents ���丮 ���� ml-agents ���� ���丮�� �����Ͻʽÿ�:

```console
cd C:\Downloads\ml-agents
```
 
������� ���� ���丮���� ������ �����Ͻʽÿ�:

```console
cd ml-agents-envs
pip install -e .
cd ..
cd ml-agents
pip install -e .
```

`-e` �÷��׸� ����Ͽ� pip�� ���� �ϸ� ���̽� ������ ���� ������ �� �ְ� `mlagents-learn`�� ������ �� �ݿ��˴ϴ�. 
`mlagents` ��Ű���� `mlagents_envs`�� �������̰�, �ٸ� ������ ��ġ�ϸ� PyPi�� ���� `mlagents_envs` �� ��ġ�� �� �ֱ� ������
�� ������� ��Ű���� ��ġ�ϴ� ���� �߿��մϴ�. 

## (������) Step 4: ML-Agents Toolkit�� ����� GPU �н� 

ML-Agents toolkit�� ���� GPU�� �ʿ����� ������ �н� �߿� PPO �˰��� �ӵ��� ũ�� ������ ���մϴ�(������ ���Ŀ� GPU�� ������ �� �� �ֽ��ϴ�).
�� ���̵�� GPU�� ����� �н��� �ϰ� ���� ��� ����ڸ� ���� ���̵� �Դϴ�. ���� GPU�� CUDA�� ȣȯ�Ǵ��� Ȯ���ؾ� �մϴ�.
[����](https://developer.nvidia.com/cuda-gpus) Nvidia ���������� Ȯ���� �ֽʽÿ�.

���� ML-Agents toolkit �� CUDA 9.0 ������ cuDNN 7.0.5 ������ �����˴ϴ�.

### Nvidia CUDA toolkit ��ġ

[Download](https://developer.nvidia.com/cuda-toolkit-archive) and install the
CUDA toolkit 9.0 from Nvidia's archive. The toolkit includes GPU-accelerated
libraries, debugging and optimization tools, a C/C++ (Step Visual Studio 2017)
compiler and a runtime library and is needed to run the ML-Agents toolkit. In
this guide, we are using version
[9.0.176](https://developer.nvidia.com/compute/cuda/9.0/Prod/network_installers/cuda_9.0.176_win10_network-exe)).

Before installing, please make sure you __close any running instances of Unity
or Visual Studio__.

Run the installer and select the Express option. Note the directory where you
installed the CUDA toolkit. In this guide, we installed in the directory
`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0`

### Install Nvidia cuDNN library

[Download](https://developer.nvidia.com/cudnn) and install the cuDNN library
from Nvidia. cuDNN is a GPU-accelerated library of primitives for deep neural
networks. Before you can download, you will need to sign up for free to the
Nvidia Developer Program.

<p align="center">
  <img src="images/cuDNN_membership_required.png"
       alt="cuDNN membership required"
       width="500" border="10" />
</p>

Once you've signed up, go back to the cuDNN
[downloads page](https://developer.nvidia.com/cudnn).
You may or may not be asked to fill out a short survey. When you get to the list
cuDNN releases, __make sure you are downloading the right version for the CUDA
toolkit you installed in Step 1.__ In this guide, we are using version 7.0.5 for
CUDA toolkit version 9.0
([direct link](https://developer.nvidia.com/compute/machine-learning/cudnn/secure/v7.0.5/prod/9.0_20171129/cudnn-9.0-windows10-x64-v7)).

After you have downloaded the cuDNN files, you will need to extract the files
into the CUDA toolkit directory. In the cuDNN zip file, there are three folders
called `bin`, `include`, and `lib`.

<p align="center">
  <img src="images/cudnn_zip_files.PNG"
       alt="cuDNN zip files"
       width="500" border="10" />
</p>

Copy these three folders into the CUDA toolkit directory. The CUDA toolkit
directory is located at
`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0`

<p align="center">
  <img src="images/cuda_toolkit_directory.PNG"
       alt="cuda toolkit directory"
       width="500" border="10" />
</p>

### Set Environment Variables

You will need to add one environment variable and two path variables.

To set the environment variable, type `environment variables` in the search bar
(this can be reached by hitting the Windows key or the bottom left Windows
button). You should see an option called __Edit the system environment
variables__.

<p align="center">
  <img src="images/edit_env_var.png"
       alt="edit env variables"
       width="250" border="10" />
</p>

From here, click the __Environment Variables__ button. Click __New__ to add a
new system variable _(make sure you do this under __System variables__ and not
User variables_.

<p align="center">
  <img src="images/new_system_variable.PNG"
       alt="new system variable"
       width="500" border="10" />
</p>

For __Variable Name__, enter `CUDA_HOME`. For the variable value, put the
directory location for the CUDA toolkit. In this guide, the directory location
is `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0`. Press __OK__ once.

<p align="center">
  <img src="images/system_variable_name_value.PNG"
       alt="system variable names and values"
       width="500" border="10" />
</p>

To set the two path variables, inside the same __Environment Variables__ window
and under the second box called __System Variables__, find a variable called
`Path` and click __Edit__. You will add two directories to the list. For this
guide, the two entries would look like:

```console
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0\lib\x64
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0\extras\CUPTI\libx64
```

Make sure to replace the relevant directory location with the one you have
installed. _Please note that case sensitivity matters_.

<p align="center">
    <img src="images/path_variables.PNG"
        alt="Path variables"
        width="500" border="10" />
</p>

### Install TensorFlow GPU

Next, install `tensorflow-gpu` using `pip`. You'll need version 1.7.1. In an
Anaconda Prompt with the Conda environment ml-agents activated, type in the
following command to uninstall TensorFlow for cpu and install TensorFlow
for gpu _(make sure you are connected to the Internet)_:

```sh
pip uninstall tensorflow
pip install tensorflow-gpu==1.7.1
```

Lastly, you should test to see if everything installed properly and that
TensorFlow can identify your GPU. In the same Anaconda Prompt, open Python 
in the Prompt by calling:

```sh
python
```

And then type the following commands:

```python
import tensorflow as tf

sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
```

You should see something similar to:

```console
Found device 0 with properties ...
```

## Acknowledgments

We would like to thank
[Jason Weimann](https://unity3d.college/2017/10/25/machine-learning-in-unity3d-setting-up-the-environment-tensorflow-for-agentml-on-windows-10/)
and
[Nitish S. Mutha](http://blog.nitishmutha.com/tensorflow/2017/01/22/TensorFlow-with-gpu-for-windows.html)
for writing the original articles which were used to create this guide.
