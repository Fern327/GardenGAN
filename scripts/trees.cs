using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class trees : MonoBehaviour
{
    public GameObject tree;
    public GameObject bush;
    public GameObject intertree;
    public GameObject lotus;
    public GameObject man;
    public GameObject woman;
    public GameObject kid;

    [Range(0, 50)]
    public int treenum = 20;
    [Range(0, 30)]
    public int treemax = 20;
    [Range(0, 10)]
    public int intertreenum = 6;
    [Range(0, 300)]
    public int bushnum = 200;

    private float width = garden_Terrian.Width();
    private static Vector2Int NNmap = garden_Terrian.NNmap();
    private int N = NNmap[0];
    private int NMap = NNmap[1];

    public Texture2D heightMap;
    public Texture2D planMap;

    // Start is called before the first frame update
    List<Vector3> treepoint;
    List<Vector3> interpoint;
    List<Vector3> bushpoint;
    List<Vector3> waterpoint;
    List<Vector3> manpoint;
    List<Vector3> womanpoint;
    List<Vector3> verts;
    List<int> indices;

    MeshRenderer meshRenderer;
    MeshFilter meshFilter;
    MeshCollider meshCollider;


    void Start()
    {
        verts = new List<Vector3>();
        indices = new List<int>();

        meshRenderer = GetComponent<MeshRenderer>();
        meshFilter = GetComponent<MeshFilter>();
        meshCollider = GetComponent<MeshCollider>();

        treepoint =new List<Vector3>();
        bushpoint = new List<Vector3>();
        interpoint = new List<Vector3>();
        waterpoint = new List<Vector3>();
        manpoint = new List<Vector3>();
        womanpoint = new List<Vector3>();
        Generate_tree();
        Generate_water();
    }

    //生成水
    public void Generate_water()
    {
        // 把数据填写好
        AddMeshData();

        // 把数据传递给Mesh，生成真正的网格
        Mesh mesh = new Mesh();
        mesh.vertices = verts.ToArray();
        //mesh.uv = uvs.ToArray();
        mesh.triangles = indices.ToArray();

        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        meshFilter.mesh = mesh;

    }

    //生成水的网格
    void AddMeshData()
    {

        Color32[] colors = planMap.GetPixels32();
        for (int z = 0; z < N; z++)
        {
            for (int x = 0; x < N; x++)
            {
                //float y = Random.Range(0, 3.5f);
                //x为采样点的采样距离，越小图片越大
                int xx = trans(x);
                int zz = trans(z);
                Vector3 p = new Vector3(x, 0, z) * width;
                verts.Add(p);
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
                int xx = trans(x);
                int zz = trans(z);
                int xx1 = trans(x + 1);
                int zz1 = trans(z + 1);
                //zz,xx左下角
                bool ifwater = garden_Terrian.def("water", colors[zz * NMap + xx].r, colors[zz * NMap + xx].g, colors[zz * NMap + xx].b);
                //zz1,xx左上角
                bool ifwater10 = garden_Terrian.def("water", colors[zz1 * NMap + xx].r, colors[zz1 * NMap + xx].g, colors[zz1 * NMap + xx].b);
                //zz1,xx1右上角
                bool ifwater11 = garden_Terrian.def("water", colors[zz1 * NMap + xx1].r, colors[zz1 * NMap + xx1].g, colors[zz1 * NMap + xx1].b);
                //zz,xx1右下角
                bool ifwater01 = garden_Terrian.def("water", colors[zz * NMap + xx1].r, colors[zz * NMap + xx1].g, colors[zz * NMap + xx1].b);
                if (ifwater || ifwater10 || ifwater11)
                {
                    indices.Add(index); indices.Add(index1); indices.Add(index2);
                }
                if (ifwater || ifwater11 || ifwater01)
                {
                    indices.Add(index); indices.Add(index2); indices.Add(index3);
                }
            }
        }

    }

    //随机生成植物
    public void Generate_tree()
    {
        //获取生成树的坐标
        Addplantpoint();
        Transform obj = GameObject.Find("trees").transform;
        int randomIndex;
        int randomint;
        for (int i = 0; i < treenum; i++)
        {
            randomIndex = Random.Range(0, treepoint.Count);
            Vector3 tpoint = treepoint[randomIndex];
            settree(tpoint, i, obj);
        }
        obj = GameObject.Find("bushs").transform;
        for (int i = 0; i < bushnum; i++)
        {
            randomIndex = Random.Range(0, treepoint.Count);
            Vector3 bpoint = treepoint[randomIndex];
            setbush(bpoint, i, obj);
        }
        obj = GameObject.Find("inters").transform;
        for (int i = 0; i < intertreenum; i++)
        {
            randomIndex = Random.Range(0, interpoint.Count);
            randomint = Random.Range(0, 1);
            if (randomint < 0.5f)
            {
                randomIndex = Random.Range(randomIndex, interpoint.Count);
            }else
            {
                randomIndex = Random.Range(0, randomIndex);
            }
            Vector3 inpoint = interpoint[randomIndex];
            setintertree(inpoint, i, obj);
        }
        randomIndex = Random.Range(0, waterpoint.Count);
        Vector3 wpoint = waterpoint[randomIndex];
        setlotus(wpoint, obj);

        //生成人
        obj = GameObject.Find("people").transform;
        for (int i = 0; i < 3; i++)
        {
            randomIndex = Random.Range(0, manpoint.Count);
            Vector3 mpoint = treepoint[randomIndex];
            setman(mpoint, i, obj,"man");
            randomIndex = Random.Range(0, womanpoint.Count);
            Vector3 wmpoint = treepoint[randomIndex];
            setman(wmpoint, i, obj, "woman");
            randomIndex = Random.Range(0, treepoint.Count);
            Vector3 kpoint = treepoint[randomIndex];
            setman(kpoint, 0, obj, "kid");
        }
    }


    //获取生成树的坐标
    void Addplantpoint()
    {
        Color32[] colors_p = planMap.GetPixels32();
        Color32[] colors_h = heightMap.GetPixels32();
        for (int z = 10; z < N - 10; z++)
        {
            for (int x = 10; x < N - 10; x++)
            {
                int xx = trans(x);
                int zz = trans(z);
                int r = colors_p[zz * NMap + xx].r;
                int g = colors_p[zz * NMap + xx].g;
                int b = colors_p[zz * NMap + xx].b;
                //在草地或者山上生成树
                if(garden_Terrian.def("grass", r, g, b)|| garden_Terrian.def("mountain", r, g, b))
                {
                    Vector3 p = new Vector3(x, colors_h[zz * NMap + xx].b/11, z) * width;
                    treepoint.Add(p);
                }
                else if(garden_Terrian.def("water", r+30, g-30, b-30)) {
                    Vector3 p = new Vector3(x,-0.4f, z) * width;
                    waterpoint.Add(p);
                }
                else if (garden_Terrian.def("corridor", r, g, b)){
                    Vector3 p = new Vector3(x, 0.5f, z) * width;
                    manpoint.Add(p);
                }
                else if(garden_Terrian.def("second", r, g, b))
                {
                    Vector3 p = new Vector3(x, 0.5f, z) * width;
                    womanpoint.Add(p);
                }
                if (z%5==0&&x%5==0&&garden_Terrian.def("inter", r, g, b))
                {
                    Vector3 p = new Vector3(x, colors_h[zz * NMap + xx].b / 11, z) * width;
                    interpoint.Add(p);
                }
            }
        }
    }

    //调用人的组件
    void setman(Vector3 point, int i, Transform obj,string str)
    {
        GameObject g = Object.Instantiate(man);
        if (str == "woman")
        {
            g = Object.Instantiate(woman);
        }else if (str == "kid")
        {
            g = Object.Instantiate(kid);
        }
        g.name = str + i;
        if (point.y < 1f)
        {
            point.y = 0f;
        }else
        {
            point.y = point.y / 2;
        }
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(1f,1f, 1f);
    }

    //调用inter树的组件
    void setintertree(Vector3 point, int i, Transform obj)
    {
        //随机宽度和高度
        float w = (Random.Range(2, 4));
        GameObject g = Object.Instantiate(intertree);
        g.name = "inter_tree" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        float h = Random.Range(1.2f, 1.8f);
        g.transform.localScale = new Vector3(w, w/h, w);
    }

    //调用树的组件
    void settree(Vector3 point,int i, Transform obj)
    {
        //随机宽度和高度
        float w = (Random.Range(4, treemax));
        w /= 10;
        GameObject g = Object.Instantiate(tree);
        g.name = "tree" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(w*1.5f, w, w*1.5f);
    }

    //调用草的组件
    void setbush(Vector3 point, int i, Transform obj)
    {
        float w = (Random.Range(1, 2));
        GameObject g = Object.Instantiate(bush);
        g.name = "bush" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(w, w, w);
    }

    //调用浮萍的组件
    void setlotus(Vector3 point, Transform obj)
    {
        GameObject g = Object.Instantiate(lotus);
        g.name = "lotus";
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(2, 1, 2);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    int trans(int x)
    {
        return Mathf.RoundToInt(x * 1.0f / N * NMap);
    }

}
