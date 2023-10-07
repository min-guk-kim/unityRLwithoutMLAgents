using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using System.IO;
using UnityEditor;

public class CSharpForGIT : MonoBehaviour
{
    Thread mThread;
    public string connectionIP = "127.0.0.1";
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;
    Vector3 receivedPos = Vector3.zero;

    // Declare a queue to handle tasks on the main thread from background threads.
    private Queue<System.Action> TODO = new Queue<System.Action>();
    bool running;

    private void Update()
    {
        // Process and execute tasks in the main thread queue.
        lock (TODO)
        {
            while (TODO.Count > 0)
            {
                TODO.Dequeue().Invoke();
            }
        }

        // Update object's position using the received data.
        transform.position = receivedPos;
    }

    private void Start()
    {
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();
    }

    void GetInfo()
    {
        localAdd = IPAddress.Parse(connectionIP);
        listener = new TcpListener(IPAddress.Any, connectionPort);
        listener.Start();

        client = listener.AcceptTcpClient();

        running = true;
        while (running)
        {
            SendAndReceiveData();
        }
        listener.Stop();
    }

    void SendAndReceiveData()
    {
        try
        {
            NetworkStream nwStream = client.GetStream();
            
            // Read data into a buffer of maximum size.
            byte[] tempBuffer = new byte[1024];
            int bytesRead = nwStream.Read(tempBuffer, 0, tempBuffer.Length);

            // Allocate appropriate buffer size based on the read data.
            byte[] buffer;
            if (bytesRead == 12) 
            {
                buffer = new byte[12];
                Array.Copy(tempBuffer, buffer, 12);
            } 
            else
            {
                buffer = new byte[1024];
                Array.Copy(tempBuffer, buffer, 1024);
            }

            if (bytesRead == 12)
            {
                receivedPos = BytesToVector3(buffer);

                // Queue a task to send the current position as a response.
                lock (TODO)
                {
                    TODO.Enqueue(() =>
                    {
                        byte[] response = Vector3ToBytes(transform.position);
                        nwStream.Write(response, 0, response.Length);
                    });
                 }
            }
            else
            {
                string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                if (message == "PING")
                    SendSignalToPython("PONG");
                else if (message == "endOfTraining")
                    lock (TODO)
                    {
                        TODO.Enqueue(() =>
                        {
                            #if UNITY_EDITOR
                            UnityEditor.EditorApplication.isPlaying = false;
                            #else
                            Application.Quit();
                            #endif
                        });
                    }
            }
        }
        catch(SocketException)
        {
            Debug.Log("Connection closed by Python.");
            running = false;  // Terminate the loop if the connection closes.
        }
        catch(IOException)
        {
            Debug.Log("IO error occurred. Possibly connection was closed by Python.");
            running = false;  // Terminate the loop if an IO error occurs.
        }
    }

    public static Vector3 BytesToVector3(byte[] bytes)
    {
        if (bytes.Length != 12)
            throw new InvalidOperationException("Invalid byte array length for Vector3 conversion.");

        float x = BitConverter.ToSingle(bytes, 0);
        float y = BitConverter.ToSingle(bytes, 4);
        float z = BitConverter.ToSingle(bytes, 8);

        return new Vector3(x, y, z);
    }

    public static byte[] Vector3ToBytes(Vector3 vector)
    {   
        byte[] bytes = new byte[12];
        BitConverter.GetBytes(vector.x).CopyTo(bytes, 0);
        BitConverter.GetBytes(vector.y).CopyTo(bytes, 4);
        BitConverter.GetBytes(vector.z).CopyTo(bytes, 8);
        return bytes;
    }

    private void OnDestroy()
    {
        SendSignalToPython("DISCONNECTED");
    }

    void SendSignalToPython(string message)
    {
        if (client != null && client.Connected)
        {
            NetworkStream nwStream = client.GetStream();
            byte[] buffer = Encoding.UTF8.GetBytes(message);
            nwStream.Write(buffer, 0, buffer.Length);
        }
    }
}