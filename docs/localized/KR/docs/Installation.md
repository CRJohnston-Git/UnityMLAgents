# ��ġ

ML-Agents�� ��ġ�ϰ� ����ϱ� ���� ����Ƽ�� ��ġ�ؾ� �ϰ� �� Repository(�����)��
Clone(����)�ϰ� �߰����Ӽ��� ������ Python(���̽�)�� ��ġ�ؾ��մϴ�. �Ʒ� Subsection(��������)������ Docker(��Ŀ) ���� �ܿ���
�� �ܰ踦 ���������� �����մϴ�.

## **Unity 2017.4** �Ǵ� ������ ������ ��ġ�Ͻʽÿ�.

[�ٿ�ε�](https://store.unity.com/kr/download)�ϰ� ��ġ�Ͻʽÿ�. ���� ������ ��Ŀ ����(���Ŀ� �Ұ���)�� ����ϰ� �ʹٸ�,
����Ƽ�� ��ġ�� ��, Linux Build Support�� �����Ͻʽÿ�.

<p align="center">
  <img src="images/unity_linux_build_support.png"
       alt="Linux Build Support"
       width="500" border="10" />
</p>

## Windows �����
Windows���� ȯ���� �����ϱ� ����, [���� ����](Installation-Windows.md)�� ���� ����� ���� �ۼ��Ͽ����ϴ�. 
Mac�� Linux�� ���� ���̵带 Ȯ�����ֽʽÿ�.

## Mac �Ǵ� Unix �����

### ML-Agents Toolkit ����� ����

����Ƽ ��ġ �Ŀ� ML-Agents Toolkit ����� ����Ҹ� ��ġ�ϰ� ���� ���Դϴ�.

```sh
git clone https://github.com/Unity-Technologies/ml-agents.git
```

`UnitySDK` ���� ���丮���� ������Ʈ�� �߰��� ����Ƽ �ּ��� ���ԵǾ� �ֽ��ϴ�.
���� �����ϴµ� ������ �Ǵ� ���� [���� ȯ��](Learning-Environment-Examples.md)���� �ֽ��ϴ�.

`ml-agents` ���� ���丮���� ����Ƽ ȯ��� �԰� ����ϴ� ���� ��ȭ�н� Ʈ���̳� ���̽� ��Ű���� ���ԵǾ� �ֽ��ϴ�.

`ml-agents-envs` ���� ���丮���� `ml-agents` ��Ű���� ���ӵǴ� ����Ƽ�� �������̽��� ���� ���̽� API�� ���ԵǾ� �ֽ��ϴ�.

`gym-unity` ���� ���丮���� OpenAI Gym�� �������̽��� ���� ��Ű���� ���ԵǾ� �ֽ��ϴ�.

### ���̽�� mlagents ��Ű�� ��ġ

ML-Agents toolkit�� ����ϱ� ���� [setup.py file](../ml-agents/setup.py)�� ������ ���Ӽ��� �Բ� ���̽� 3.6�� �ʿ��մϴ�.
�ֿ� ���Ӽ��� �Ϻδ� ������ �����մϴ�:

- [TensorFlow](Background-TensorFlow.md) (Requires a CPU w/ AVX support)
- [Jupyter](Background-Jupyter.md)

Python 3.6�� ���� ��ġ�Ǿ� ���� �ʴٸ�, [�ٿ�ε�](https://www.python.org/downloads/)�ϰ� ��ġ�Ͻʽÿ�.

���� ����� ���̽� ȯ���� `pip3`�� �������� �ʴ´ٸ�, ����
[���û���](https://packaging.python.org/guides/installing-using-linux-tools/#installing-pip-setuptools-wheel-with-linux-package-managers)
�� ���� ��ġ�Ͻʽÿ�.

���Ӽ��� `mlagents` ���̽� ��Ű���� ��ġ�ϱ� ���� ���� ��ɾ �����Ͻʽÿ�:

```sh
pip3 install mlagents
```

�� ��ɾ ���� PyPi�� ����(������ ����Ұ� �ƴ�) `ml-agents`�� ��ġ�� ���Դϴ�. 
���� ���������� ��ġ�� �Ϸ� �ߴٸ�, `mlagents-learn --help` ��ɾ ������ �� ���� ���Դϴ�.
��ɾ �����ϸ� ����Ƽ �ΰ�� `mlagents-learn`���� ����� �� �ִ� ��ɾ� ���� �Ű��������� �� �� �ֽ��ϴ�. 

**����:**

- ���� Python 3.7 �Ǵ� Python 3.5�� �������� �ʽ��ϴ�.
- ���� Anaconda�� ����ϰ� TensorFlow�� ������ �ִٸ�, ���� 
  [��ũ](https://www.tensorflow.org/install/pip)���� Anaconda ȯ�濡�� ��� TensorFlow�� ��ġ�ϴ��� Ȯ���Ͻʽÿ�.
### ������ ���� ��ġ���

���� `ml-agents` �Ǵ� `ml-agents-envs`�� �����ϰ� �ʹٸ�, PyPi�� �ƴ� ������ ����ҷ� ���� ��Ű���� ��ġ�ؾ� �մϴ�.
�̸� ����, `ml-agents`�� `ml-agents-envs`�� ���� ��ġ�ؾ� �մϴ�. ������� ��Ʈ ���丮���� ���� ��ɾ �����Ͻʽÿ�:

```sh
cd ml-agents-envs
pip3 install -e ./
cd ..
cd ml-agents
pip3 install -e ./
```

`-e` �÷��׸� ����Ͽ� pip�� ���� �ϸ� ���̽� ������ ���� ������ �� �ְ� `mlagents-learn`�� ������ �� �ݿ��˴ϴ�.
`mlagents` ��Ű���� `mlagents_envs`�� �������̰�, �ٸ� ������ ��ġ�ϸ� PyPi�� ���� `mlagents_envs`��
��ġ�� �� �ֱ� ������ �� ������� ��Ű���� ��ġ�ϴ� ���� �߿��մϴ�. 

## ��Ŀ ��� ��ġ

���� ML-Agents�� ���� ��Ŀ�� ����ϰ� �ʹٸ�, [�� ���̵�](Using-Docker.md)�� �����Ͻʽÿ�.

## ���� �ܰ�

[���� ���̵�](Basic-Guide.md) ���������� ����Ƽ ������ ML-Agents toolkit�� ���� �� �н��� �� ����, 
ȯ�� ����, �н� ����� ���� ���� ª�� Ʃ�丮���� �����ϰ� �ֽ��ϴ�.

## ����

ML-Agents�� ���õ� ������ �߻��ϸ� ������ [FAQ](FAQ.md)�� [���� ����](Limitations.md) �������� ������ �ֽʽÿ�.
���� ������ ���� �ƹ��͵� ã�� �� ���ٸ� OS, Pythons ���� �� ��Ȯ�� ���� �޼����� �Բ� [�̽� ����](https://github.com/Unity-Technologies/ml-agents/issues)�� ���ֽʽÿ�.
