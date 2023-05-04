---
categories: "TIL-codestates"
tag: [ "inputstream", "outputstream", "filereader", "filewriter"]
---



# Input/Output Stream

자바에서는 입출력을 다루기 위한 InputStream, OutputStream을 제공합니다. 스트림은 단방향으로만 데이터를 전송할 수 있기에, 입력과 출력을 동시에 처리하기 위해서는 각각의 스트림이 필요합니다.

## FileInputStream

먼저 ocdestates.txt 파일을 생성합니다. 파일 내용은 임의로 `codestate!!` 로 하겠습니다.

그리고 아래처럼 FileInputStream 으로 해당 파일을 읽겠습니다.

```java
public static void main(String args[])
        {
                try {
                        FileInputStream fileInput = new FileInputStream("codestates.txt");

                        ArrayList<Integer> list = new ArrayList<>();
                        int i = 0;
                     	//fileInput.read()의 리턴값을 i에 저장한 후, 값이 -1인지 확인합니다.
                        while ((i = fileInput.read()) != -1) {
                                System.out.print((char)i);
                                list.add(i);
                        }
                        fileInput.close();
                        System.out.println(list);
                }
                catch (Exception e) {
                        System.out.println(e);
                }
        }
```

이렇게 하면 결과는 아래와 같이 나옵니다.

```
 
 [255, 254, 99, 0, 111, 0, 100, 0, 101, 0, 115, 0, 116, 0, 97, 0, 116, 0, 101, 0, 33, 0, 33, 0, 13, 0, 10, 0]
```

UTF-16 으로 인코딩되다보니 각 글자가 2byte 라서 `0` 이 따라붙었구요. 앞에 `255, 254, 99, 0, 111, 0` 와 뒤에 `13, 0, 10, 0` 는 다음을 의미합니다.

- `255, 254`: BOM for UTF-16 Little Endian
- `99, 0`: 'c' in UTF-16 Little Endian
- `111, 0`: 'o' in UTF-16 Little Endian
- ...
- `13, 0`: carriage return (CR) in UTF-16 Little Endian
- `10, 0`: line feed (LF) in UTF-16 Little Endian

BufferedInputStream이라는 보조 스트림을 사용하면 성능이 향상되기 때문에, 대부분은 이를 사용합니다. 버퍼란 바이트 배열로서, 여러 바이트를 저장하여 한 번에 많은 양의 데이터를 입출력할 수 있도록 도와주는 임시 저장 공간이라고 이해하면 됩니다.

```java
public static void main(String args[])
        {
                try {
                        FileInputStream fileInput = new FileInputStream("codestates.txt");
                    	BufferedInputStream bufferedInput = new BufferedInputStream(fileInput);


                        ArrayList<Integer> list = new ArrayList<>();
                        int i = 0;
                     	//fileInput.read()의 리턴값을 i에 저장한 후, 값이 -1인지 확인합니다.
                        while ((i = bufferedInput.read()) != -1) {
                                System.out.print((char)i);
                                list.add(i);
                        }
                        fileInput.close();
                        System.out.println(list);
                }
                catch (Exception e) {
                        System.out.println(e);
                }
        }
```

출력결과는 똑같습니다.

## FileOutputStream

FileOutputStream 을 파일을 출력해줍니다.

```java
import java.io.FileOutputStream;
  
public class FileOutputStreamExample {
    public static void main(String args[]) {
        try {
            FileOutputStream fileOutput = new FileOutputStream("codestates.txt");
            String word = "code";

            byte b[] = word.getBytes();
            fileOutput.write(b);
            fileOutput.close();
        }
        catch (Exception e) {
            System.out.println(e);
        }
    }
}
```

위 코드를 실행하면 "codestates.txt" 파일이 생성되고, "code" 라는 내용을 가집니다.

# FileReader / FileWriter

Input/OutputStream 은 바이트 기반으로 입출력 단위가 1byte 입니다. 하지만 Java에서 char 타입은 2byte 입니다. 이를 해소하기 위해 자바에서는 문자 기반 스트림을 제공합니다. 문자 기반 스트림에는 FileReader와 FileWriter가 있습니다.

FileReader는 인코딩을 유니코드로 변환하고, FileWriter는 유니코드를 인코딩으로 변환합니다. 

## FileReader

```java
public class FileReaderExample {
    public static void main(String args[]) {
        try {
            String fileName = "codestates.txt";
            FileReader file = new FileReader(fileName);

            int data = 0;

            while((data=file.read()) != -1) {
                System.out.print((char)data);
            }
            file.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

출력결과는 'code' 입니다. ("codestates.txt" 내용) 

바이트 기반 스트림과 마찬가지로, Reader에도 성능을 개선할 수 있는 BufferedReader가 있습니다.

```java
public class BufferedReaderExample {
    public static void main(String args[]) {
        try {
            String fileName = "codestates.txt";
            FileReader file = new FileReader(fileName);
            BufferedReader buffered = new BufferedReader(file);

            int data = 0;

            while((data=buffered.read()) != -1) {
                System.out.print((char)data);
            }
            file.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }
```

## FileWriter

앞서 만든 codestates.txt파일에 “written!”이라는 문자열을 입력하는 예제입니다.

```java
public class FileWriterExample {
    public static void main(String args[]) {
        try {
            String fileName = "codestates.txt";
            FileWriter writer = new FileWriter(fileName);

            String str = "written!";
            writer.write(str);
            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```



# File

자바에서는 File 클래스로 파일과 디렉토리에 접근할 수 있습니다.

```java
import java.io.File;
import java.io.IOException;

public class FileExample {
        public static void main(String args[]) throws IOException {
                File file = new File("../codestates.txt");

                System.out.println(file.getPath()); //파일 경로 : ..\codestates.txt
                System.out.println(file.getParent()); //상위 폴더 : ..
                System.out.println(file.getCanonicalPath()); // 절대 경로 : C:\Users\kimhobeen\IdeaProjects\codeStates\codestates.txt
                System.out.println(file.canWrite()); //쓰기 가능 여부 : false
        }
}
```

다음과 같이 파일 일스턴스를 통해 파일을 생성할 수 있습니다.

```java
File file = new File("./", "newCodestates.txt"); //경로, 이름
file.createNewFile();
```

다음은 현재 디렉토리(.)에서 확장자가 .txt인 파일만을 대상으로, 파일명 앞에 “code”라는 문자열을 붙여주는 예제입니다.

```java
import java.io.File;

public class FileClassExample {
    public static void main(String[] args) {

        File parentDir = new File("./");
        File[] list = parentDir.listFiles();

        String prefix = "code";

        for(int i =0; i <list.length; i++) {
            String fileName = list[i].getName();

						if(fileName.endsWith("txt") && !fileName.startsWith("code")) {
                list[i].renameTo(new File(parentDir, prefix + fileName));
            }
        }
    }
}

```