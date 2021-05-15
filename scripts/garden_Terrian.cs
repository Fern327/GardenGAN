using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;  //操作文件夹时需引用该命名空间
using System.Text;

public class garden_Terrian : MonoBehaviour
{
    public static float width = 0.3f;
    public static int N = 256;
    public static int NMap =512;

    MeshRenderer meshRenderer;
    MeshFilter meshFilter;
    MeshCollider meshCollider;

    // 用来存放顶点数据
    List<Vector3> verts;
    List<int> indices;
    List<Color> rgbs;
    //存储横放廊道边缘的坐标点
    List<Vector3> conts_x;
    //存储竖放廊道边缘的坐标点
    List<Vector3> conts_y;

    //public static string plan_path = Application.streamingAssetsPath + "/testpic/compare2/multis_plan.png";
    //public static string height_path = Application.streamingAssetsPath + "/testpic/compare2/multis_gh.png";
    public GameObject corridor;
    public Texture2D heightMap;
    public Texture2D planMap;
    public Gradient gradient;
    private float maxHeight = 0.0f;
    private float minHeight = 255.0f;

    private void Awake()
    {
    }

    private void Start()
    {
        verts = new List<Vector3>();
        indices = new List<int>();
        rgbs = new List<Color>();
        conts_x = new List<Vector3>();
        conts_y = new List<Vector3>();

        meshRenderer = GetComponent<MeshRenderer>();
        meshFilter = GetComponent<MeshFilter>();
        meshCollider = GetComponent<MeshCollider>();

        Generate();
        Generate_Corridor();
    }

    //生成廊道
    public void Generate_Corridor()
    {
        //获取廊道边缘坐标信息
        AddpointData();
        Transform obj = GameObject.Find("corridors").transform;
        for (int i = 0; i < conts_x.Count; i++)
        {
            setobject(conts_x[i], false, i, obj);
        }
        for (int i = 0; i < conts_y.Count; i++)
        {
            setobject(conts_y[i], true, i, obj);
        }
    }

    //判断是否是廊道边缘
    int ifcontour(int x, int z, Color32[] colors_p)
    {

        int xx = trans(x - 1);
        int zz = trans(z - 1);
        int xx1 = trans(x);
        int zz1 = trans(z);
        int xx2 = trans(x + 1);
        int zz2 = trans(z + 1);
        int res = 0;
        //左边
        int r1 = colors_p[zz1 * NMap + xx].r;
        int g1 = colors_p[zz1 * NMap + xx].g;
        int b1 = colors_p[zz1 * NMap + xx].b;
        //上边
        int r2 = colors_p[zz2 * NMap + xx1].r;
        int g2 = colors_p[zz2 * NMap + xx1].g;
        int b2 = colors_p[zz2 * NMap + xx1].b;
        //右边
        int r3 = colors_p[zz1 * NMap + xx2].r;
        int g3 = colors_p[zz1 * NMap + xx2].g;
        int b3 = colors_p[zz1 * NMap + xx2].b;
        //下边
        int r4 = colors_p[zz * NMap + xx1].r;
        int g4 = colors_p[zz * NMap + xx1].g;
        int b4 = colors_p[zz * NMap + xx1].b;
        if (!def("corridor", r1, g1, b1))
        {
            //左边有一块不是
            res = 0;
        }
        else if (!def("corridor", r2, g2, b2))
        {
            //上边有一块不是
            res = 1;
        }
        else
        {
            res = 2;
        }
        return res;
    }

    //存储廊道的位置点
    void AddpointData()
    {
        Color32[] colors_p = planMap.GetPixels32();
        float y = 0.35f;
        //收集同一纵坐标的四个边缘点的横坐标
        //List<int> X = new List<int>();;
        //收集同一横坐标的四个边缘点的纵坐标
        //List<int> Z = new List<int>();
        for (int z = 1; z < N - 1; z++)
        {
            for (int x = 1; x < N - 1; x++)
            {
                int xx = trans(x);
                int zz = trans(z);
                int r = colors_p[zz * NMap + xx].r;
                int g = colors_p[zz * NMap + xx].g;
                int b = colors_p[zz * NMap + xx].b;
                if (def("corridor", r, g, b))
                {
                    int res = ifcontour(x, z, colors_p);
                    if (res == 0)
                    {
                        if (z % 3 == 0)
                        {
                            Vector3 p = new Vector3(x + 1.5f, y, z) * width;
                            conts_x.Add(p);
                        }
                    }
                    if (res == 1)
                    {
                        if (x % 3 == 0)
                        {
                            Vector3 p = new Vector3(x, y, z - 1.5f) * width;
                            conts_y.Add(p);
                        }
                    }
                }
            }
        }
    }

    //设置廊道组件
    void setobject(Vector3 point, bool rotate, int i, Transform obj)
    {
        Vector3 rotation;
        GameObject g = Object.Instantiate(corridor);
        if (rotate)
        {
            rotation = new Vector3(0, 90, 0);
            g.name = "corridor_y" + i;
        }
        else
        {
            rotation = new Vector3(0, 0, 0);
            g.name = "corridor_x" + i;
        }
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = rotation;
        g.transform.localScale = new Vector3(1, 1, 2);
    }


    //生成
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
        rgbs.Clear();
        indices.Clear();
    }

    int trans(int x)
    {
        return Mathf.RoundToInt(x * 1.0f / N * NMap);
    }

    //判断是哪个区块
    public static bool def(string s, int r, int g, int b)
    {
        bool res = false;
        //if (s == "mountain" && r > 30 && r < 130 && g < 100 && b < 100)
        //
        //res = true;
        //}
        //if (s == "landscape" && r > 130 && r < 215 && g > 205 && b > 205)
        //{
        //res = true;
        //}
        //if (s == "water" && r < 100 && g > 180 && b > 180)
        //{
        // res = true;
        //}
        //if (s == "corridor" && r > 150 && g < 120 && b < 120)
        //{
        //res = true;
        //}
        //if (s == "main" && r > 210 && g > 100 && g < 200 && b > 20 && b < 100)
        //{
        //res = true;
        //}
        //if (s == "other" && r < 50 && g < 50 && b < 50)
        //{
        //res = true;
        //}
        //if (s == "grass" && r > 180 && g > 180 && b < 80)
        //{
        //res = true;
        //}
        if (s == "mountain" && r < 30 && g < 30)
        { 
            res = true;
        }
        if (s == "inter" && r > 90 && r < 190 && g > 200)
        {
            res = true;
        }
        if (s == "landscape" && r < 90 && g > 90 && g < 190)
        {
            res = true;
        }
        if (s == "water" && r > 200 && g > 200 && b<80)
        {
             res = true;
        }
        if (s == "corridor" && r > 230 && g < 20)
        {
            res = true;
        }
        if (s == "main" && r > 90 && r < 190 && g < 70)
        {
            res = true;
        }
        if (s == "other" && r > 90 && r < 190 && g > 90 && g < 190)
        {
            res = true;
        }
        if (s == "grass" && r < 80 && g > 190 )
        {
            res = true;
        }
        if(s=="second"&& r > 210&&g > 100 && g < 180)
        {
            res = true;
        }
        if (s == "outside" && r > 200 && g > 200 && b > 200)
        {
            res = true;
        }
        return res;
    }

    //返回width的值
    public static float Width()
    {
        return width;
    }

    //返回[N,Nmap]
    public static Vector2Int NNmap()
    {
        Vector2Int nnmap = new Vector2Int(N, NMap);
        return nnmap;
    }

    //判断网格三角形差距是不是太大，减少尖锐角度出现
    bool judge(int r, int r1, int r2, int r3)
    {
        if (r - r1 > 150 || r - r2 > 150 || r - r3 > 150)
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    //判断石峰各坐标偏移的高度，偏向低矮的那个方向
    string stoneorient(int x,int z,Color32[] colors)
    {
        int xx = trans(x);
        int zz = trans(z);
        int xx1 = trans(x + 1);
        int zz1 = trans(x + 1);
        int xx0 = trans(x - 1);
        int zz0 = trans(x - 1);
        string res="none";
        float min = 0;
        float h = colors[zz * NMap + xx].b;
        float h_left = colors[zz * NMap + xx0].b;
        float h_right = colors[zz * NMap + xx1].b;
        float h_top = colors[zz1 * NMap + xx].b;
        float h_bottom = colors[zz0 * NMap + xx].b;
        if (h > h_left)
        {
            min = h - h_left;
            res = "left";
        }
        if (h > h_right&& h - h_right>min)
        {
            min = h - h_right;
            res = "right";
        }
        if (h > h_top && h - h_top > min)
        {
            min = h - h_top;
            res = "top";
        }
        if (h > h_bottom && h - h_bottom > min)
        {
            min = h - h_bottom;
            res = "bottom";
        }
        return res;
    }

    //获取网格坐标信息
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
                int xx1;
                int zz1;
                float y = colors[zz * NMap + xx].b / 12f;
                if (x < N - 1 && z < N - 1)
                {
                    xx1 = trans(x + 1);
                    zz1 = trans(z + 1);
                    int R = colors[zz * NMap + xx].b;
                    int r1 = colors[zz1 * NMap + xx].b;
                    int r2 = colors[zz1 * NMap + xx1].b;
                    int r3 = colors[zz * NMap + xx1].b;
                    if (judge(R, r1, r2, r3))
                    {
                        y = R / 25.0f;
                    }
                }
                int r = colors_p[zz * NMap + xx].r;
                int g = colors_p[zz * NMap + xx].g;
                int b = colors_p[zz * NMap + xx].b;
                bool ifwater = def("water", r, g, b);
                //if (def("water", r, g, b) || def("mountain", r, g, b) || def("main", r, g, b) || def("landscape", r, g, b) || def("other", r, g, b))
                if (!(ifwater|| def("mountain", r, g, b)||def("second",r,g,b)))
                {
                    y = 1.0f;
                }
                if (ifwater)
                {
                    y = -2.0f;
                }
                Vector3 p = new Vector3(x, y, z) * width;
                string res="";
                if (y > 8f)
                {
                    int stonex = x;
                    int stonez = z;
                    if (x < N - 1 && x > 0 && z > 0 && z < N - 1)
                    {
                        res=stoneorient(x, z, colors);
                        //Debug.Log(res);
                    }
                    if (res == "left")
                    {
                        stonex = x - Random.Range(0, 3) ;
                    }else if (res == "right")
                    {
                        stonex = x + Random.Range(0, 3);
                    }
                    else if (res == "top")
                    {
                        stonez = z + Random.Range(0, 3);
                    }
                    else if (res == "bottom")
                    {
                        stonez = z - Random.Range(0, 3);
                    }
                    p = new Vector3(stonex, y, stonez) * width;
                }
                if (colors[zz * NMap + xx].b > maxHeight) { maxHeight = colors[zz * NMap + xx].b; }
                if (colors[zz * NMap + xx].b < minHeight) { minHeight = colors[zz * NMap + xx].b; }
                verts.Add(p);
            }
        }

        //按照高度着色
        for (int z = 0; z < N; z++)
        {
            for (int x = 0; x < N; x++)
            {
                int index = z * N + x;
                float y = verts[index].y * 12;
                float p = (y - minHeight) / (maxHeight - minHeight);
                int r = colors_p[trans(z) * NMap + trans(x)].r;
                int g = colors_p[trans(z) * NMap + trans(x)].g;
                int b = colors_p[trans(z) * NMap + trans(x)].b;
                int basenum = 255;
                Color c;
                if (def("mountain", r, g, b))
                {
                    c = gradient.Evaluate(p);
                }
                //else if (def("main", r, g, b))
                //{
                    //c = new Color((float)14 / basenum, (float)55 / basenum, (float)84 / basenum, 1);
                //}
                //else if (def("corridor", r, g, b))
                //{
                    //c = new Color((float)50 / basenum, (float)50 / basenum, (float)50 / basenum, 1);
                //}
                //else if (def("other", r, g, b) || def("landscape", r, g, b))
                //{
                    //c = new Color((float)0 / basenum, (float)0 / basenum, (float)0 / basenum, 1);
                //}
                else if (def("grass", r, g, b))
                {
                    c = new Color((float)61 / basenum, (float)92 / basenum, (float)62 / basenum, 1);
                }
                else if (def("water", r, g, b))
                {
                    c = new Color((float)76 / basenum, (float)123 / basenum, (float)149 / basenum, 1);
                }
                else if (def("second", r, g, b))
                {
                    c = new Color((float)180 / basenum, (float)180 / basenum, (float)180 / basenum, 1);
                }
                else if (def("inter", r, g, b))
                {
                    c = new Color((float)122 / basenum, (float)130 / basenum, (float)60 / basenum, 1);
                }
                else
                {
                    c = new Color((float)255 / basenum, (float)255 / basenum, (float)255 / basenum, 1);
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
                int xx = trans(x);
                int zz = trans(z);
                int xx1 = trans(x + 1);
                int zz1 = trans(z + 1);
                //zz,xx自己
                bool ifoutside = def("outside", colors_p[zz * NMap + xx].r, colors_p[zz * NMap + xx].g, colors_p[zz * NMap + xx].b);
                //zz1,xx左上角
                bool ifoutside10 = def("outside", colors_p[zz1 * NMap + xx].r, colors_p[zz1 * NMap + xx].g, colors_p[zz1 * NMap + xx].b);
                //zz1,xx1右上角
                bool ifoutside11 = def("outside", colors_p[zz1 * NMap + xx1].r, colors_p[zz1 * NMap + xx1].g, colors_p[zz1 * NMap + xx1].b);
                //zz,xx1右下角
                bool ifoutside01 = def("outside", colors_p[zz * NMap + xx1].r, colors_p[zz * NMap + xx1].g, colors_p[zz * NMap + xx1].b);
                if (!(ifoutside && ifoutside01 && ifoutside10 && ifoutside11))
                {
                    indices.Add(index); indices.Add(index1); indices.Add(index2);
                    indices.Add(index); indices.Add(index2); indices.Add(index3);
                }
                
                //if (def("water", r, g, b) || colors[zz * NMap + xx].b > 0 || colors[zz1 * NMap + xx].b > 0 || colors[zz1 * NMap + xx1].b > 0)
                //{
                //indices.Add(index); indices.Add(index1); indices.Add(index2);
                //}
                //if (def("water", r, g, b) || colors[zz * NMap + xx].b > 0 || colors[zz1 * NMap + xx].b > 0 || colors[zz * NMap + xx1].b > 0)
                //{
                //indices.Add(index); indices.Add(index2); indices.Add(index3);
                //}
                //indices.Add(index); indices.Add(index1); indices.Add(index2);
                //indices.Add(index); indices.Add(index2); indices.Add(index3);
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

