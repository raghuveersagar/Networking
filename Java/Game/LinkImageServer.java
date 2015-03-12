import java.awt.Button;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.EventQueue;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.LayoutManager;
import java.awt.Point;
import java.awt.RenderingHints;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.rmi.Naming;
import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JSplitPane;

/*This class acts as server.It is used to play as player 1.
 * It has inner classes extending Jpanels which form different 
 * sections on the screen.
 * 
 */
public class LinkImageServer implements Runnable {

	int buttonWidth = 100;
	int buttonHeight = 100;
	int imageSetSelected;
	JLabel labelP1;
	JLabel labelP2;
	List<ImageButton> imageButtonList = new ArrayList<ImageButton>();
	private final String IMAGE_SET_PATH = "images/imageSets";
	private final String IMAGE_SOLUTIONS_PATH = "images/solutions";
	private final String GAME_OVR_IMAGE_PATH = "images/misc/gameover.jpg";
	private final String P1_WINS_IMAGE_PATH = "images/misc/p1.jpg";
	private final String P2_WINS_IMAGE_PATH = "images/misc/p2.jpg";
	private final String START_AGAIN_IMAGE_PATH = "images/misc/startAgain.jpg";
	Map<String, JButton> imageButtonMap = new HashMap<String, JButton>();
	RemoteInfo info = null;
	JPanel topImageSetPanel;
	String playerAnswerStatus;
	JPanel bottomImageSetPanel;
	JSplitPane imageSetSplitPane;
	JFrame frame;
	JLabel answerStatusLabel;
	JButton imageSetNextButton;
	JPanel solutionPanel;
	boolean player1sTurn = true;
	boolean player2sTurn = false;
	boolean IsGameOver = false;
	int player1Score = 0;
	int player2Score = 0;
	String inputLine;
	PrintWriter out;
	boolean alienClick = false;

	@Override
	public void run() {

		int portNumber = Integer.parseInt("16000");

		try {
			ServerSocket serverSocket = new ServerSocket(portNumber);
			Socket clientSocket = serverSocket.accept();
			out = new PrintWriter(clientSocket.getOutputStream(), true);
			BufferedReader in = new BufferedReader(new InputStreamReader(
					clientSocket.getInputStream()));

			while ((inputLine = in.readLine()) != null) {

				Registry r = 	LocateRegistry.getRegistry("localhost");
				RemoteInfo obj = (RemoteInfo)r.lookup("clientObj");	
				 inputLine = obj.getInfo();
				String[] userData = inputLine.split("-");
				String code = userData[0];
				String data = userData[1];
				alienClick = true;
				if (code.equals("200"))
					imageButtonMap.get(data).doClick();
				else if (code.equals("300")) {
					imageSetNextButton.setEnabled(true);
					imageSetNextButton.doClick();
				}

			}

		} catch (IOException e) {
			System.out
					.println("Exception caught when trying to listen on port "
							+ portNumber + " or listening for a connection");
			System.out.println(e.getMessage());
		}
		catch (NotBoundException ne) {
			
			System.out.println(ne.getMessage());
		}

	}

	public static void main(String[] args) {


        
        
        //System.out.println("HelloServer bound in registry");
    
		
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
			public void run() {
				LinkImageServer l = new LinkImageServer();
				l.go();
				Thread t = new Thread(l);
				t.start();
			}
		});

	}

	void go() {

		frame = new JFrame("Find the linking image: Player 1");
		topImageSetPanel = new ImageSetPanel();
		bottomImageSetPanel = new AnswerStatusPanel();
		solutionPanel = new ImageSolutionPanel();
		JPanel playerInfoPanel = new PlayerInfoPanel();

		imageSetSplitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT,
				topImageSetPanel, bottomImageSetPanel);
		imageSetSplitPane.setDividerLocation(400);
		imageSetSplitPane.setDividerSize(0);

		JSplitPane solutionssplitPane = new JSplitPane(
				JSplitPane.VERTICAL_SPLIT, solutionPanel, playerInfoPanel);
		solutionssplitPane.setDividerLocation(400);
		solutionssplitPane.setDividerSize(0);
		JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT,
				imageSetSplitPane, solutionssplitPane);
		// splitPane.setOneTouchExpandable(true);
		splitPane.setDividerLocation(250);
		splitPane.setDividerSize(0);

		// Provide minimum sizes for the two components in the split pane.
		// Dimension minimumSize = new Dimension(600, 600);
		// listScrollPane.setMinimumSize(minimumSize);
		// pictureScrollPane.setMinimumSize(minimumSize);

		// Provide a preferred size for the split pane.
		splitPane.setPreferredSize(new Dimension(600, 600));
		frame.setContentPane(splitPane);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setSize(600, 600);
		frame.setVisible(true);

	}

	public class ImageSetPanel extends JPanel {

		List<Image> list = new ArrayList<Image>();
		String pathTillSET;
		File file;
		int numberOfSets = 0;
		int numberOfImageFiles = 0;
		int index = 1;
		int width = 0;
		int height = 0;
		int noOfFirstRowImages = 2;
		int noOfSecondRowImages = 0;

		ImageSetPanel() {
			file = new File(IMAGE_SET_PATH);
			String[] fileArray = file.list();

			numberOfSets = fileArray.length;

		}

		@Override
		protected void paintComponent(Graphics g) {

			int imageSetStartX = 20;
			int imageSetStartY = 100;
			int imageWidth = 100;
			int imageHeight = 100;
			int distanceBetweenImagesX = 20;
			int distanceBetweenImagesY = 40;

			if (index <= numberOfSets) {
				Color c = g.getColor();

				imageSetSelected = index++;
				pathTillSET = IMAGE_SET_PATH + "/Set" + imageSetSelected;
				setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
				file = new File(pathTillSET);

				String[] setImagesArray = file.list();

				g.setColor(getBackground());
				g.fillRect(0, 0, getWidth(), getHeight());
				numberOfImageFiles = setImagesArray.length;
				g.drawImage(
						new ImageIcon(pathTillSET + "/" + setImagesArray[0])
								.getImage(), imageSetStartX, imageSetStartY,
						imageWidth, imageHeight, this);
				g.setColor(getBackground());
				g.fillRect(imageSetStartX + imageWidth, imageSetStartY,
						distanceBetweenImagesX, imageHeight);
				g.drawImage(
						new ImageIcon(pathTillSET + "/" + setImagesArray[1])
								.getImage(), imageSetStartX + imageWidth
								+ distanceBetweenImagesX, imageSetStartY,
						imageWidth, imageHeight, this);

				g.drawImage(
						new ImageIcon(pathTillSET + "/" + setImagesArray[2])
								.getImage(), imageSetStartX, imageSetStartY
								+ imageHeight + distanceBetweenImagesY,
						imageWidth, imageHeight, this);
				g.setColor(getBackground());
				g.fillRect(
						imageSetStartX + imageWidth + distanceBetweenImagesX,
						imageSetStartY + imageHeight, distanceBetweenImagesX,
						imageHeight);

				if (numberOfImageFiles == 4)
					g.drawImage(new ImageIcon(pathTillSET + imageSetSelected
							+ "/" + setImagesArray[3]).getImage(),
							imageSetStartX + imageWidth
									+ distanceBetweenImagesX, imageSetStartY
									+ imageHeight + distanceBetweenImagesY,
							imageWidth, imageHeight, this);
			} else {
				g.drawImage(new ImageIcon(GAME_OVR_IMAGE_PATH).getImage(), 0,
						0, getWidth(), getHeight(), this);
				IsGameOver = true;
				solutionPanel.repaint();
			}
		}
	}

	public class ImageSolutionPanel extends JPanel {

		List<Image> imageList = new ArrayList<Image>();

		int frameWidth;
		int frameHeight;
		int panelWidth;
		int panelheight;

		int numberofButtonsInRow = 5;
		int numberofButtonsInColumn = 5;
		int width;
		int height;

		public ImageSolutionPanel() {

			int index = 0;

			ImageButton iButton;

			File file = new File(IMAGE_SOLUTIONS_PATH);
			String[] imageFileList = file.list();
			ImageButtonAdapter iButtonMouseAdapter = new ImageButtonAdapter();
			int noOfImages = imageFileList.length;
			for (String x : imageFileList)

			{

				iButton = new ImageButton(new ImageIcon(
						getScaledImage(new ImageIcon(IMAGE_SOLUTIONS_PATH + "/"
								+ x).getImage(), 100, 100)), x);
				iButton.addActionListener(iButtonMouseAdapter);

				imageButtonMap.put(x, iButton);

				if (!x.contains(".db"))
					add(iButton);
				imageButtonList.add(iButton);

			}

		}

		private Image getScaledImage(Image srcImg, int w, int h) {
			BufferedImage resizedImg = new BufferedImage(w, h,
					BufferedImage.TYPE_INT_RGB);
			Graphics2D g2 = resizedImg.createGraphics();
			g2.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
					RenderingHints.VALUE_INTERPOLATION_BILINEAR);
			g2.drawImage(srcImg, 0, 0, w, h, null);
			g2.dispose();
			return resizedImg;
		}

		@Override
		protected void paintComponent(Graphics g) {
			if (IsGameOver) {
				String path;

				if (player1Score > player2Score)
					path = P1_WINS_IMAGE_PATH;
				else if (player1Score < player2Score)
					path = P2_WINS_IMAGE_PATH;
				else
					path = START_AGAIN_IMAGE_PATH;
				for (ImageButton ib : imageButtonList)
					ib.setVisible(false);

				g.drawImage(new ImageIcon(path).getImage(), 0, 0, getWidth(),
						getHeight(), this);
			}
		}

	}

	class ImageButton extends JButton {
		public ImageButton(ImageIcon icon, String name) {
			super(icon);
			setName(name);
		}

		@Override
		public Dimension getPreferredSize() {
			// TODO Auto-generated method stub
			return new Dimension(buttonWidth, buttonHeight);
		}

	}

	class PlayerInfoPanel extends JPanel {

		PlayerInfoPanel() {

			setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

			labelP1 = new JLabel("Player 1 :");
			labelP1.setPreferredSize(new Dimension(50, 50));
			labelP2 = new JLabel("Player 2:");
			labelP1.setFont(new Font("Serif", Font.PLAIN, 50));
			labelP2.setFont(new Font("Serif", Font.PLAIN, 30));
			labelP1.setForeground(Color.GREEN);
			labelP2.setForeground(Color.RED);
			add(labelP1);
			add(labelP2);

		}

	}

	class ImageButtonAdapter implements ActionListener {

		@Override
		public void actionPerformed(ActionEvent ae) {

			JButton b = (JButton) ae.getSource();

			String temp = new String(imageSetSelected + ".jpg");

			String buttonName = b.getName();

			if (!alienClick)
			{
				
				
				try {
					info= new RemoteImpl();
					info.putInfo("200-" + buttonName);
					Naming.rebind("serverObj", info);
					out.println("200-" + buttonName);
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			if (buttonName.equalsIgnoreCase(temp))
				playerAnswerStatus = "Correct";
			else
				playerAnswerStatus = "Wrong";

			answerStatusLabel.setText(playerAnswerStatus);
			if (player1sTurn) {

				if (playerAnswerStatus.equalsIgnoreCase("Correct"))
					player1Score += 10;
				player1sTurn = false;
				player2sTurn = true;
			} else if (player2sTurn) {

				if (playerAnswerStatus.equalsIgnoreCase("Correct"))
					player2Score += 10;
				player1sTurn = true;
				player2sTurn = false;
			}
			labelP1.setText("Player 1 :" + String.valueOf(player1Score));
			labelP2.setText("Player 2 :" + String.valueOf(player2Score));
			if (!alienClick)
				imageSetNextButton.setEnabled(true);

		}

	}

	class AnswerStatusPanel extends JPanel {
		public AnswerStatusPanel() {

			setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
			imageSetNextButton = new JButton("Next");
			imageSetNextButton.setPreferredSize(new Dimension(100, 50));
			imageSetNextButton.setAlignmentX(Component.CENTER_ALIGNMENT);

			imageSetNextButton.setEnabled(false);
			imageSetNextButton.addActionListener(new ActionListener() {

				@Override
				public void actionPerformed(ActionEvent e) {
					// TODO Auto-generated method stub
					imageSetNextButton.setEnabled(false);
					if (player1sTurn) {
						labelP1.setFont(new Font("Serif", Font.PLAIN, 50));
						labelP2.setFont(new Font("Serif", Font.PLAIN, 30));
						labelP1.setForeground(Color.GREEN);
						labelP2.setForeground(Color.RED);
					}
					if (player2sTurn) {
						labelP2.setFont(new Font("Serif", Font.PLAIN, 50));
						labelP1.setFont(new Font("Serif", Font.PLAIN, 30));
						labelP1.setForeground(Color.RED);
						labelP2.setForeground(Color.GREEN);
					}
					if (!alienClick){
						

						
						//out.println("200-" + buttonName);
						try {
							info= new RemoteImpl();
							info.putInfo("300-Temp");
							Naming.rebind("serverObj", info);
							out.println("300-Temp");
						} catch (Exception e1) {
							// TODO Auto-generated catch block
							e1.printStackTrace();
						}
					
					}
					alienClick = false;
					topImageSetPanel.repaint();
				}
			});
			add(imageSetNextButton);
			answerStatusLabel = new JLabel(playerAnswerStatus, JLabel.CENTER);
			answerStatusLabel.setFont(new Font("Serif", Font.PLAIN, 50));
			answerStatusLabel.setPreferredSize(new Dimension(100, 220));
			add(answerStatusLabel);
			answerStatusLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
			answerStatusLabel.setAlignmentY(Component.BOTTOM_ALIGNMENT);

		}

	}

}
