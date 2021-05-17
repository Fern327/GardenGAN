using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class mountain_Terrian : MonoBehaviour
{
    private float width = 0.3f;
    private int N = 256;
    public int NMap = 512;

    MeshRenderer meshRenderer;
    MeshFilter meshFilter;
    MeshCollider meshCollider;

    // 用来存放顶点数据
    List<Vector3> verts;
    List<int> indices;
    List<Color> rgbs;

    public Texture2D heightMap;
    public Texture2D planMap;
    public Gradient gradient;
    private float maxHeight = 0.0f;
    private float minHeight = 255.0f;


    private void Awake()
    {
    }

    Transform water;

    private void Start()
    {
        verts = new List<Vector3>();
        indices = new List<int>();
        rgbs = new List<Color>();

        meshRenderer = GetComponent<MeshRenderer>();
        meshFilter = GetComponent<MeshFilter>();
        meshCollider = GetComponent<MeshCollider>();

        //mountain = GameObject.Find("mountain").transform;
        //mountain.Translate(new Vector3(0, 0, 0));

        Generate();

        

    }

    public void Generate()
    {
        ClearMeshData();

        // 把数据填写好
        AddMeshData();

        // 把数据传递给Mesh，生成真正的网格
        Mesh mesh = new Mesh();
        mesh.vertices = verts.ToArray();
        //mesh.uv = uvs.ToArray();
        mesh.triangles = indices.ToArray();
        mesh.colors = rgbs.ToArray();

        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        meshFilter.mesh = mesh;
        // 碰撞体专用的mesh，只负责物体的碰撞外形
        //meshCollider.sharedMesh = mesh;
    }

    void ClearMeshData()
    {
        verts.Clear();
        indices.Clear();
    }
    
    int trans(int x)
    {
        return Mathf.RoundToInt(x * 1.0f / N * NMap);
    }
    void AddMeshData()
    {
        
        Color32[] colors = heightMap.GetPixels32();
        Color32[] colors_p = planMap.GetPixels32();
        for (int z = 0; z < N; z++)
        {
            for (int x = 0; x < N; x++)
            {
                //float y = Random.Range(0, 3.5f);
                //x为采样点的采样距离，越小图片越大
                int xx = trans(x);
                int zz = trans(z);
                int r = colors_p[zz * NMap + xx].r;
                int g = colors_p[zz * NMap + xx].g;
                int b = colors_p[zz * NMap + xx].b;
                float y = 0f;
                if (garden_Terrian.def("mountain", r, g, b))
                {
                    //y = colors[zz * NMap + xx].b / 10f;
                    y = colors[zz * NMap + xx].b / 10f;
                    if (y > maxHeight) { maxHeight = y; }
                    if (y < minHeight) { minHeight = y; } 
                }
                Vector3 p = new Vector3(x, y, z) * width;
                verts.Add(p);
            }
        }

        for (int z = 0; z < N; z++)
        {
            for (int x = 0; x < N ; x++)
            {
                int index = z * N + x;
                float y = verts[index].y/width;
                Color c;
                if (y > 0)
                {
                    float p = (y - minHeight) / (maxHeight - minHeight);
                    c = gradient.Evaluate(p);
                }else
                {
                    c=new Color((float)1, (float)1, (float)1, 0);
                }
                rgbs.Add(c);
            }
        }
        
        for (int z = 0; z < N - 1; z++)
        {
            for (int x = 0; x < N - 1; x++)
            {
                int index = z * N + x;  //左下角
                int index1 = (z + 1) * N + x;  //左上角
                int index2 = (z + 1) * N + x + 1;  //右上角
                int index3 = z * N + x + 1;   //右下角
                indices.Add(index); indices.Add(index1); indices.Add(index2);
                indices.Add(index); indices.Add(index2); indices.Add(index3);
            }
        }

    }

    //float lastUpdateTime = 0;
    //private void Update()
    //{
    //if (Time.time >= lastUpdateTime + 0.1f)
    //{
    //Generate();
    //lastUpdateTime = Time.time;
    //}
    //}
}

