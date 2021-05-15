using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;  //操作文件夹时需引用该命名空间
using System.Text;


public class Architecture : MonoBehaviour
{
    public GameObject main;
    public GameObject other;
    public GameObject landscape;
    public string arcpath;
    private float width = garden_Terrian.Width();
    private static Vector2Int NNmap = garden_Terrian.NNmap();
    private int N = NNmap[0];
    private int Nmap = NNmap[1];

    // Start is called before the first frame update
    void Start()
    {
        Generate_arcs();
    }
    
    //读取各建筑的数据,根据数据调用建筑生成建筑
    void Generate_arcs()
    {
        //string path = arcpath;
        //逐行读取返回的为数组数据
        string[] strs = File.ReadAllLines(arcpath);
        for (int i=6;i<strs.Length;i+=7)
        {
            string str = strs[i-6];
            float px;
            float py;
            float x;
            float y;
            float h;
            float angle;
            float.TryParse(strs[i-5], out px);
            float.TryParse(strs[i - 4], out py);
            float.TryParse(strs[i - 3], out x);
            float.TryParse(strs[i - 2], out y);
            float.TryParse(strs[i - 1], out h);
            float.TryParse(strs[i], out angle);
            px = ((px)* N / Nmap) * width;
            py = ((Nmap - py) * N / Nmap) * width;
            float height = 1.5f;
            //判断出山上的建筑
            if (h > 160f)
            {
                if (str == "main")
                {
                    height = (h - 125f)/10f* width;
                    h = 125f;
                }
                else if (str == "landscape")
                {
                    height = (h - 90f) / 10f * width;
                    h = 90f;
                }else
                {
                    height = (h - 100f) / 10f * width;
                    h = 100f;
                }
            }
            Vector3 point = new Vector3(px, height, py);
            setarcs(point, i / 6, str, x, y, h, angle);
        }
    }

    void setarcs(Vector3 point, int i, string obj,float x, float y,float h,float angle)
    {
        float scale_x;
        float scale_y;
        float scale_h;
        GameObject g;
        if (obj == "main")
        {
            g = Object.Instantiate(main);
            scale_x = ((x*N/ Nmap) / 20.0f)*100;
            scale_y = ((y * N / Nmap) / 12.0f)*100;
            scale_h = (((h / 10.0f)/10.0f)*0.3f)*100;
            angle = -180.0f + angle;
        }
        else if (obj == "landscape")
        {
            g = Object.Instantiate(landscape);
            //scale_x = ((x * N / Nmap) / 5.0f)*300;
            //scale_y = ((y * N / Nmap) / 5.0f)*350;
            //scale_h = (((h / 10.0f) / 6.0f) * 0.3f)*200;
            scale_x = ((x * N / Nmap) / 3.6f)*1f;
            scale_y = ((y * N / Nmap) / 3.6f)*1f;
            scale_h = (((h / 10.0f) / 4.6f) * 0.3f)*1f;
            angle = angle;
            //point=new Vector3(point.x-0.17f,point.y,point.z-3f);
            point = new Vector3(point.x , point.y-1.3f, point.z );
        }
        else 
        {
            g = Object.Instantiate(other);
            scale_y = ((x * N / Nmap) / 11.5f)*150;
            scale_x = ((y * N / Nmap) / 9.5f)*150;
            scale_h = (((h / 10.0f) / 8.0f) * 0.3f)*130;
            point.y += 1.0f;
            angle = 90.0f + angle;
        }
        g.name =obj + i;
        Transform parent = GameObject.Find("architectures").transform;
        g.transform.SetParent(parent);
        g.transform.localPosition = point;
        g.transform.localEulerAngles = new Vector3(0, angle, 0);
        g.transform.localScale = new Vector3(scale_x* width, scale_h*1.5f, scale_y * width);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
