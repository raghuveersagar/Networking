import java.rmi.RemoteException;


public class RemoteImpl implements RemoteInfo {

	private String info=null;
	public RemoteImpl() throws RemoteException {
	
}
	
	
	@Override
	public String getInfo() throws RemoteException {
		
		return info;
	}
	
	@Override
	public void putInfo(String info) throws RemoteException
	{
		this.info=info;
		
	}

}
