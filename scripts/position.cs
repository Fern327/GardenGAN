using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class position : MonoBehaviour
{
    Transform obj;
    void Start()
    {
        obj = GameObject.Find("water").transform;
        obj.localPosition = new Vector3(0, -0.2f, 0);
        obj = GameObject.Find("garden").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("foundation").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("corridors").transform;
        obj.localPosition = new Vector3(0, 0.2f, 0);
        obj = GameObject.Find("trees").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("bushs").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("architectures").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("dottrees").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("grouptrees").transform;
        obj.localPosition = new Vector3(0, 0, 0);
        obj = GameObject.Find("people").transform;
        obj.localPosition = new Vector3(0, 0, 0);
    }
}
