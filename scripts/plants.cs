using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class plants : MonoBehaviour
{
    public GameObject group_tree;
    public GameObject dot_tree;
    public GameObject bush;
    public GameObject intertree;
    public GameObject lotus;
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
    public Texture2D plantsMap;

    // Start is called before the first frame update
    List<Vector3> group_treepoint;//Ⱥֲ��
    List<Vector3> dot_treepoint;//��ֲ��
    List<Vector3> interpoint;
    List<Vector3> bushpoint;
    List<Vector3> waterpoint;
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

        group_treepoint = new List<Vector3>();
        dot_treepoint = new List<Vector3>();
        bushpoint = new List<Vector3>();
        interpoint = new List<Vector3>();
        waterpoint = new List<Vector3>();
        Generate_tree();
        Generate_water();
    }

    //����ˮ
    public void Generate_water()
    {
        // ��������д��
        AddMeshData();

        // �����ݴ��ݸ�Mesh����������������
        Mesh mesh = new Mesh();
        mesh.vertices = verts.ToArray();
        //mesh.uv = uvs.ToArray();
        mesh.triangles = indices.ToArray();

        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        meshFilter.mesh = mesh;

    }

    //����ˮ������
    void AddMeshData()
    {

        Color32[] colors = planMap.GetPixels32();
        for (int z = 0; z < N; z++)
        {
            for (int x = 0; x < N; x++)
            {
                //float y = Random.Range(0, 3.5f);
                //xΪ������Ĳ������룬ԽСͼƬԽ��
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
                int index = z * N + x;  //���½�
                int index1 = (z + 1) * N + x;  //���Ͻ�
                int index2 = (z + 1) * N + x + 1;  //���Ͻ�
                int index3 = z * N + x + 1;   //���½�
                int xx = trans(x);
                int zz = trans(z);
                int xx1 = trans(x + 1);
                int zz1 = trans(z + 1);
                //zz,xx���½�
                bool ifwater = garden_Terrian.def("water", colors[zz * NMap + xx].r, colors[zz * NMap + xx].g, colors[zz * NMap + xx].b);
                //zz1,xx���Ͻ�
                bool ifwater10 = garden_Terrian.def("water", colors[zz1 * NMap + xx].r, colors[zz1 * NMap + xx].g, colors[zz1 * NMap + xx].b);
                //zz1,xx1���Ͻ�
                bool ifwater11 = garden_Terrian.def("water", colors[zz1 * NMap + xx1].r, colors[zz1 * NMap + xx1].g, colors[zz1 * NMap + xx1].b);
                //zz,xx1���½�
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

    //����ֲ��
    public void Generate_tree()
    {
        //��ȡ�����ɵ�ֲ�ʹ�ֲ��
        Adddtreespoint();
        //��ȡ���ɹ�ľ������
        Addplantpoint();
        int randomIndex;
        int randomint;
        Transform obj = GameObject.Find("bushs").transform;
        for (int i = 0; i < bushnum; i++)
        {
            randomIndex = Random.Range(0, bushpoint.Count);
            Vector3 bpoint = bushpoint[randomIndex];
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
            }
            else
            {
                randomIndex = Random.Range(0, randomIndex);
            }
            Vector3 inpoint = interpoint[randomIndex];
            setintertree(inpoint, i, obj);
        }
        randomIndex = Random.Range(0, waterpoint.Count);
        Vector3 wpoint = waterpoint[randomIndex];
        setlotus(wpoint, obj);
    }


    //����ֲ��İ뾶
    int plantscale(int x,int z,Color32[] colors,bool ifdot)
    {
        int r_dot = 512;
        int r = 0;
        int tree;
        if (ifdot)
        {
            tree = 1;
        }else
        {
            tree = 0;
        }
        //�ұ�Ѱ�뾶
        for (int i = 1; i + x < NMap; i++)
        {
            if (colors[z * NMap + x+i][tree] < 180)
            {
                r_dot = i;
            }else
            {
                break;
            }
        }
        r = r_dot;
        //���Ѱ�뾶
        for(int i = 1; x-i >0 && i<=r; i++)
        {
            if (colors[z * NMap + x-i][tree] < 180)
            {
                r_dot = i;
            }
            else
            {
                break;
            }
        }
        r = r_dot;
        //�ϱ�Ѱ�뾶
        for (int i = 1; i + z < NMap && i <= r; i++)
        {
            if (colors[(z+i) * NMap + x ][tree] < 180)
            {
                r_dot = i;
            }
            else
            {
                break;
            }
        }
        r = r_dot;
        //�±�Ѱ�뾶
        for (int i = 1; z - i > 0 && i <= r; i++)
        {
            if (colors[(z - i) * NMap + x][tree] < 180)
            {
                r_dot = i;
            }
            else
            {
                break;
            }
        }
        r = r_dot;
        return r;
    }


    //��ȡ���ɵ�ֲ��Ⱥֲ�������겢���ɵ�ֲ��Ⱥֲ��
    void Adddtreespoint()
    {
        Color32[] colors_plant = plantsMap.GetPixels32();
        Color32[] colors_h = heightMap.GetPixels32();
        Transform groupobj = GameObject.Find("grouptrees").transform;
        Transform dotobj = GameObject.Find("dottrees").transform;
        int groupid = 0;
        int dotid = 0;
        for (int z = 1; z < NMap-3; z++)
        {
            for (int x = 1; x < NMap-3; x++)
            {
                //ʶ��Ⱥֲ��ľ
                float xx = Mathf.RoundToInt(x * 1.0f / NMap * N) * width;
                float zz = Mathf.RoundToInt(z * 1.0f / NMap * N) * width;
                float y = colors_h[z * NMap + x].b / 12f * width;
                if (y > 0.8f)
                {
                    y = 0.8f;
                }
                if (colors_plant[z * NMap + x].r < 10&& colors_plant[z * NMap + x-1].r > 10 && colors_plant[(z+1) * NMap + x].r > 10 )
                {
                    int group_r = plantscale(x, z, colors_plant, false);
                    int h = colors_plant[(z+2) * NMap + x+2].r;
                    Vector3 point = new Vector3(xx, y+0.5f, zz);
                    setgrouptree(point, groupid, group_r,h, groupobj);
                    groupid++;
                }
                if (colors_plant[z * NMap + x].g < 10 && colors_plant[z * NMap + x - 1].g > 10 && colors_plant[(z + 1) * NMap + x].g > 10)
                {
                    int dot_r = plantscale(x, z, colors_plant, true);
                    int h = colors_plant[(z + 2) * NMap + x + 2].g;
                    Vector3 point = new Vector3(xx, y, zz);
                    setdottree(point, dotid, dot_r,h, dotobj);
                    dotid++;
                }
            }
        }

    }


    //��ȡ���ɹ�ľ������
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
                //�ڲݵػ���ɽ��������
                if (garden_Terrian.def("grass", r, g, b) || garden_Terrian.def("mountain", r, g, b))
                {
                    Vector3 p = new Vector3(x, colors_h[zz * NMap + xx].b / 12, z) * width;
                    bushpoint.Add(p);
                }
                else if (garden_Terrian.def("water", r + 30, g - 30, b - 30))
                {
                    Vector3 p = new Vector3(x, -0.4f, z) * width;
                    waterpoint.Add(p);
                }
                if (z % 5 == 0 && x % 5 == 0 && garden_Terrian.def("inter", r, g, b))
                {
                    Vector3 p = new Vector3(x, colors_h[zz * NMap + xx].b / 10, z) * width;
                    interpoint.Add(p);
                }
            }
        }
    }


    //����inter�������
    void setintertree(Vector3 point, int i, Transform obj)
    {
        //�����Ⱥ͸߶�
        float w = (Random.Range(2, 4));
        GameObject g = Object.Instantiate(intertree);
        g.name = "inter_tree" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        float h = Random.Range(1.2f, 1.8f);
        g.transform.localScale = new Vector3(w, w / h, w);
    }

    //���õ�ֲ�������
    void setdottree(Vector3 point, int i,int r,float h, Transform obj)
    {
        //�����Ⱥ͸߶�
        //��ֲ���뾶Ϊ2.1m,�߶�Ϊ6.8m��
        float w = r * 120f / 512f / 2.1f;
        float z = h / 15f / 6.7f;
        GameObject g = Object.Instantiate(dot_tree);
        g.name = "dot_tree_" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(w, z, w);
    }

    //����Ⱥֲ�������
    void setgrouptree(Vector3 point, int i, int r, float h, Transform obj)
    {
        //�����Ⱥ͸߶�
        //�����Ⱥ͸߶�
        //Ⱥֲ���뾶Ϊ0.56m,�߶�Ϊ2.38m��
        float w = r * 120f / 512f / 0.56f;
        float z = h / 15f / 2.38f;
        GameObject g = Object.Instantiate(group_tree);
        g.name = "group_tree_" + i;
        g.transform.SetParent(obj);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, 0, 0);
        g.transform.localScale = new Vector3(w, z, w);
    }


    //���òݵ����
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

    //���ø�Ƽ�����
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
