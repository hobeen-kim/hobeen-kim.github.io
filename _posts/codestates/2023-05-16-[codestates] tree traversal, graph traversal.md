---
categories: "codestates"
tag: [ "tree traversal", "graph traversal"]
---

# 트리 순회

트리 순회에는 전위(preorder traverse), 중위(inorder traverse), 후위(postorder traversal) 순회가 있습니다. 

## preorder traverse

전위 순회는 루트 -> 왼쪽 -> 오른쪽 순서대로 방문합니다.

```java
public ArrayList<String> preOrder(Node node, ArrayList<String> list) {
    if (node != null) {
      list.add(node.getData());
      list = preOrder(node.getLeft(), list);
      list = preOrder(node.getRight(), list);
    }
    return list;
}
```

- 여기서 먼저 순회를 시작할 node 의 data 를 저장한 후 재귀함수를 통해 Left 를 순회합니다.
- 이후 right 를 순회한 뒤 list 를 반환합니다.
  

## inorder traverse

중위 순회는 왼쪽 -> 루트 -> 오른쪽 순서대로 방문합니다.

```java
public ArrayList<String> preOrder(Node node, ArrayList<String> list) {
    if (node != null) {
      list = preOrder(node.getLeft(), list);
      list.add(node.getData());
      list = preOrder(node.getRight(), list);
    }
    return list;
}
```

- 왼쪽 노드를 다 방문한 후 루트를 방문하고, 오른쪽 노드를 방문합니다.

​	

## postorder traverse

후위 순회는 왼쪽 -> 오른쪽 -> 루트 순서대로 방문합니다.

```java
public ArrayList<String> postOrder(Node node, ArrayList<String> list) {
    if (node != null) {
      list = postOrder(node.getLeft(), list);
      list = postOrder(node.getRight(), list);
      list.add(node.getData());
    }
    return list;
}
```



# 그래프 순회

그래프 탐색은 정점부터 시작해 그래프의 **모든 정점들을 한 번씩 방문(탐색)하는 것이 목적**입니다. 그래프 탐색에는 가까운 정점부터 탐색하는 **BFS**(Breadth-First Search, 너비우선탐색)  **DFS**(Depth-First Search, 깊이우선탐색) 가 있습니다. 


## BFS

BFS 는 큐를 사용하여 구현됩니다. BFS 에서는 시작 정점을 큐에 삽입한 후, 인접한 정점을 큐에 차례대로 삽입하면서 탐색을 진행합니다. 특징은 다음과 같습니다.

- 최단 경로 탐색에 유리합니다.
- 방문한 정점들을 저장해야 하는 경우 메모리 사용이 큽니다. 따라서 그래프의 크기가 큰 경우에는 BFS 보다 DFS 를 사용해야 합니다.
- 그래프의 밀도가 높거나(간선의 개수가 많거나) 그래프의 크기가 크면(정점의 개수가 많으면) BFS 의 성능이 떨어집니다.
- visited 배열과 같은 방문 여부를 체크하는 자료 구조를 사용해야 합니다.

다음과 같이 구현할 수 있습니다.

```java
/**
     * BFS 인접행렬 : 너비 우선 탐색을 구현한 템플릿 예제입니다.
     *
     * @param array : 각 정점을 행/열로 하고, 연결된 정점은 1로, 연결되지 않은 정점은 0으로 표기하는 2차원 배열
     * @param visited : 방문여부 확인을 위한 배열
     * @param src : 방문할 정점
     * @param result : 방문했던 정점 리스트를 저장한 List
     *
     **/
    public ArrayList<Integer> bfs_array(int[][] array, boolean[] visited, int src, ArrayList<Integer> result) {
        //bfs의 경우 큐를 사용합니다.
	    Queue<Integer> queue = new LinkedList<>();
        //시작 지점을 큐에 넣어주고, 해당 버택스의 방문 여부를 변경합니다.
	    queue.offer(src);
	    visited[src] = true;
        //큐에 더이상 방문할 요소가 없을 경우까지 반복합니다.
	    while (!queue.isEmpty()) {
            //현재 위치를 큐에서 꺼낸 후
	      int cur = queue.poll();
            // 현재 방문한 정점을 result에 삽입합니다.
				result.add(cur);
        //전체 배열에서 현재 버택스의 행만 확인합니다.
	      for (int i = 0; i < array[cur].length; i++) {
            //길이 존재하고, 아직 방문하지 않았을 경우
	        if(adjArray[cur][i] == 1 && !visited[i]) {
                //큐에 해당 버택스의 위치를 넣어준 이후
	          queue.offer(i);
                //방문 여부를 체크합니다.
	          visited[i] = true;
	        }
	      }
	    }
			//이어진 모든 길을 순회한 후 방문 여부가 담긴 ArrayList를 반환합니다.
	    return result;
  }
```



## BFS 활용

- 최단 거리를 구해야 하는 경우
- 검색 대상의 규모가 크지 않고, 검색 시작 지점으로부터 원하는 대상이 별로 멀지 않은 경우

위 두가지 경우에 BFS 를 사용하면 유리합니다. 아래에서 최단 경로를 찾는 문제를 살펴보겠습니다.

먼저 입력입니다.

```java
int[][] graph = {
            {0, 1, 1, 0, 0, 0},
            {1, 0, 0, 1, 1, 0},
            {1, 0, 0, 0, 0, 1},
            {0, 1, 0, 0, 0, 0},
            {0, 1, 0, 0, 0, 1},
            {0, 0, 1, 0, 1, 0}
        };
int start = 0;
int end = 5;

shortestPath(graph, start, end); // [0, 2, 5]
```

로직입니다.

```java
public ArrayList<Integer> shortestPath(int[][] graph, int start, int end) {
  boolean[] visited = new boolean[graph.length];
  return bfs(graph, start, end, visited);
}

public ArrayList<Integer> bfs(int[][] graph, int start, int end, boolean[] visited) {
  //bfs의 경우 큐를 사용합니다.
  Queue<Integer> queue = new LinkedList<>();
  //i번째 인덱스의 부모노드를 저장합니다. ex) parent[1] = 2 --> 1 의 부모노드는 2
  int[] parent = new int[graph.length];

  //큐에 start 를 저장합니다.
  queue.offer(start);
  //start 방문을 체크합니다.
  visited[start] = true;
  // start 의 부모노드는 없으므로 -1 을 저장합니다.
  parent[start] = -1;

  
  while (!queue.isEmpty()) {
    //현재 노드를 큐에서 빼옵니다.
    int node = queue.poll();

    // 도착점까지 도달한다면
    if (node == end) {
      //반환할 list 를 만듭니다.
      ArrayList<Integer> path = new ArrayList<>();
      while (node != -1) {
        //path 에 현재 노드를 저장합니다.
        path.add(node);
        //parent 를 통해 현재노드의 부모노드로 올라갑니다.
        node = parent[node];
      }
      // 도착점 -> 시작점 순으로 저장되어있으므로 뒤집어줍니다.
      Collections.reverse(path);
      return path;
    }

    //현재 노드에서 방문 가능한 모든 노드를 저장합니다.
    for (int i = 0; i < graph.length; i++) {
      if (graph[node][i] == 1 && !visited[i]) {
        //노드 i 를 큐에 저장합니다.
        queue.add(i);
        //i 번째 visited 를 true 로 변경합니다.
        visited[i] = true;
        //i 번째 부모노드를 현재 노드로 설정합니다.
        parent[i] = node;
      }
    }
  }
  // 끝까지 길을 찾기 못한 경우, null을 반환.
  return null;
}
```



## DFS

DFS 는 **스택 또는 재귀**를 이용하여 구현할 수 있습니다. 특징은 다음과 같습니다.

- BFS 보다 탐색 시간은 오래 걸릴지라도 모든 정점을 완전히 탐색할 수 있습니다.
- 현 경로 상의 정점들만 기억하면 되므로 저장 공간의 수요가 비교적 적습니다.
- 목표한 정점이 깊은 단계에 있으면 값을 빨리 구할 수 있습니다.
- 깊이 우선 탑색은 그래프 내의 순환구조를 고려하여 이미 방문한 정점을 다시 방문하지 않도록 해야합니다.
- 찾아낸 길이 최단 경로가 된다는 보장이 없습니다.

DFS 는 일반적으로 재귀를 통해 구현합니다.

```java
**
     * DFS 인접행렬 : 깊이 우선 탐색을 구현한 템플릿 예제입니다.
     *
     * @param array : 각 정점을 행/열로 하고, 연결된 정점은 1로, 연결되지 않은 정점은 0으로 표기하는 2차원 배열
     * @param visited : 방문 여부 확인을 위한 배열
     * @param node : 방문할 정점
     * @param result : 방문했던 정점 리스트를 저장한 List
     *
     **/
    public ArrayList<Integer> dfs(int[][] array, boolean[] visited, int node, ArrayList<Integer> result) {
        // 이미 방문했다면
        if (visited[node] == true) {
                result.add(node);    // 방문한 정점을 저장
                return result;      // 저장한 데이터를 반환하며, 재귀호출을 종료
            }

        // 아직 방문하지 않았다면
        visited[node] = true;	// 방문한 정점을 표기
        
		// 현재 정점에서 이동할 수 있는 정점을 순회하며 재귀 호출
        for (int index = 0; index < array.length; index++) {
            if (array[node][i] == 1) {
            	// 재귀 호출을 통해, 방문 여부를 담은 데이터를 반환과 동시에 할당
            	result = dfs(array, visited, i, result);
            }
        }
        return result;
    }
```



## DFS 활용

- 경로의 특징을 저장해야 하는 경우
  - 예를 들면 각 정점에 숫자가 적혀있고 a부터 b까지 가는 경로를 구하는데 경로에 같은 숫자가 있으면 안 된다는 문제 등, 각각의 경로마다 특징을 저장해 둬야 할 때는 DFS를 사용합니다. (BFS는 경로의 특징을 가지지 못합니다)
- 미로 문제
- 검색 대상이 클 경우

다음은 2차원 배열에서 섬의 개수는 구하는 문제입니다. 2차원 배열에서 1은 땅을 나타내고, 0은 물을 나타냅니다.상하좌우 인접한 땅은 같은 섬으로 간주합니다. 이 때 섬의 개수를 구하는 알고리즘입니다.

**입력**

```java
int grid[][] = new int[][]{
	{"1","1","1","0","0"},
  {"1","1","0","0","0"},
  {"1","1","0","0","1"},
  {"0","0","0","1","1"}
};

numIslands(grid) // 2
```

**로직**

```java
class Solution {
    public int numIslands(char[][] grid) {
        // 입력된 grid가 비어있을 경우, 섬이 존재하지 않으므로 0을 반환합니다.
        if (grid == null || grid.length == 0) {
            return 0;
        }

        int numIslands = 0; // 섬의 수를 담을 변수를 선언, 초기화
        int numRows = grid.length; // Row의 최대 길이
        int numCols = grid[0].length; //Col의 최대 길이

        // 대륙을 순회합니다. 이중 loop
        for (int i = 0; i < numRows; i++) {
            for (int j = 0; j < numCols; j++) {
                // 현재 방문한 정점이 1이라면(섬이라면)
                if (grid[i][j] == '1') {
                    numIslands++; // 섬의 수를 증가시키고
                    dfs(grid, i, j); // DFS를 호출하여 주변의 이어진 섬이 있는지 확인한 후 모두 0 으로 변경합니다.
                }
            }
        }

        return numIslands;
    }

    private void dfs(char[][] grid, int row, int col) {
        // 섬의 최대 길이 확인
        int numRows = grid.length;
        int numCols = grid[0].length;

        // 이동 후, 섬의 크기를 벗어난 경우(예외 처리)
        if (row < 0 || col < 0 || row >= numRows || col >= numCols || grid[row][col] == '0') {
            return;
        }

        // 현재 방문한 땅을 0 할당(방문 여부 체크)
        grid[row][col] = '0';

        // Down, Up, Right, Left 이동을 재귀 호출을 통해서 처리
        dfs(grid, row + 1, col);
        dfs(grid, row - 1, col);
        dfs(grid, row, col + 1);
        dfs(grid, row, col - 1);
    }
}
```