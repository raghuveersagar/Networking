import java.rmi.Remote;


public interface RemoteInfo extends Remote {
	String getInfo() throws java.rmi.RemoteException;
	void putInfo(String info) throws java.rmi.RemoteException;
}


