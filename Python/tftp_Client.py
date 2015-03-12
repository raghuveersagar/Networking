import socket
import struct
import timeit

BASE_FORMAT_RRQ = "!H"
OPCODE_RRQ = 1
OPCODE_DATA = 3
OPCODE_ACK = 4
OPCODE_ERROR = 5
FORMAT_ACK = "!HH"
FORMAT_DATA = "!HH"
_MODE_ = "octet"


# This method implements the get functionality of TFTP
def get (host_name, port, file_name):
    start_timer = timeit.default_timer()
    total_time_while1 = 0
    total_time_while2 = 0
    port=int(port) 
    file_ondisk = open(file_name, 'w')
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.settimeout(2);
    actual_format = BASE_FORMAT_RRQ + str(len(file_name)) + 'sx' + str(len(_MODE_)) + 'sx' 
    packet_RRQ = struct.pack(actual_format, OPCODE_RRQ, file_name, _MODE_)
    client_sock.sendto(packet_RRQ, (host_name, port))
    
    serviceNameError = 0
    timeoutError = 0
    get_more_data = True;
    previous_block_num_recv = 0;
    retries = 0;
    total_len = 0
    last_packet_sent = packet_RRQ;
    packet_count = 0
    while get_more_data:
        start_timer_while1 = timeit.default_timer()
        # This loop handles timeouts
        while 1:
            try:
                (packet_RECEIVED, (host_name, port)) = client_sock.recvfrom(65536)
                packet_count += 1
                retries = 0;
                break;
            except socket.timeout:
                timeoutError += 1
                retries = retries + 1;
                client_sock.sendto(last_packet_sent, (host_name, port))
                if (retries == 4):
                    retries = 0;
                    print('Transfer timed out.')
                    client_sock.close()
                    return
        stop_timer_while1 = timeit.default_timer()
        total_time_while1 += (stop_timer_while1 - start_timer_while1)
        opcode, = struct.unpack("!H", packet_RECEIVED[:2]);
        # print("opcode "+str(opcode))
        total_len = len(packet_RECEIVED)
        # handle error packets
        if int(opcode) == OPCODE_ERROR:
            error_code, = struct.unpack("!H", packet_RECEIVED[2:4]);
            error_msg, = struct.unpack("!" + str(total_len - 5) + "s", packet_RECEIVED[4:total_len - 1]);
            print("Error code " + str(error_code) + ": " + error_msg)
            client_sock.close()
            return
        # print('total_len' + str(total_len))
        if(total_len < 516):
            get_more_data = False
        (opcode, block_num_recv, data) = struct.unpack(FORMAT_DATA + str(total_len - 4) + 's', packet_RECEIVED)
        if(block_num_recv <= previous_block_num_recv):
            continue;
        previous_block_num_recv = block_num_recv;
        if opcode == 3:
            
            file_ondisk.write(data)
            packet_ACK = struct.pack(FORMAT_ACK, OPCODE_ACK, block_num_recv)
            start_timer_while2 = timeit.default_timer()
            # print('Send ACK'+str(block_num_recv))
            # client_sock.setblocking(False)
            # client_sock.sendto(packet_ACK, (host_name, port))
            
            # here we send ACKs to received data packets
            while 1:
                try:
                    client_sock.sendto(packet_ACK, (host_name, port))
                    retries = 0;
                    break;
                except socket.gaierror:
                    serviceNameError += 1
                    retries = retries + 1;
                    if(retries == 4):
                        retries = 0;
                        raise socket.gaierror;
            stop_timer_while2 = timeit.default_timer()
            last_packet_sent = packet_ACK;
            
            total_time_while2 += stop_timer_while2 - start_timer_while2
    stop_timer = timeit.default_timer()
    print('Received ' + str(packet_count * 512 + total_len + (packet_count + 1) * 4) + ' bytes in %0.2f seconds' % (stop_timer - start_timer))
    # print('serviceNameError'+str(serviceNameError))
    # print('timeoutError'+str(timeoutError))
    # print('total_time_while1 '+str(total_time_while1))
    # print('total_time_while2 '+str(total_time_while2))
    client_sock.close()        
    file_ondisk.close()



    
    



def main():
    host_name = ""
    port = ""
    hostname_resolved = False
    while 1:
        print 'tftp>' ,
        user_says = raw_input()
        command = user_says.split();
        if(len(command) > 1 and  command[0] == 'connect'):
            host_name = command[1]
            if len(command) == 3:
                port = command[2]
            else:
                port = 69
            
            try:
                socket.gethostbyname(host_name)
                hostname_resolved = True
            except socket.error:
                print(host_name + ': unknown host')    
                
             
        elif(len(command) == 2 and command[0] == 'get'):
            if not hostname_resolved:
                print(host_name + ': unknown host')
            else:
                get(host_name, port, command[1])
    
        elif(command[0] == 'quit'):
            break;
        elif(command[0] == '?'):
            print 'connect     connect to remote tftp'
            print 'get         receive file'
            print 'quit        exit tftp'
            print '?           print help information'
        else:
            print'?Invalid command/ Invalid command args'     


main()

