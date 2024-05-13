#!/usr/bin/python3
import curses
import yaml
import argparse
import os
import time

def main(stdscr, docker_compose_file):
    # Turn off cursor blinking
    curses.curs_set(0)
    
    # Clear the screen
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Display instructions
    stdscr.addstr(1, 1, "Use arrow keys to navigate, Space to select, and Enter to submit")
    
    # Load Docker Compose file
    with open(docker_compose_file, 'r') as file:
        try:
            docker_compose = yaml.safe_load(file)
            services = list(docker_compose["services"].keys())
            
        except yaml.YAMLError as exc:
            stdscr.addstr(2, 0, f"Error loading Docker Compose file: {exc}")
            stdscr.getch()
            return
    
    # Create a checklist
    selected = [False] * len(services)
    current_row = 2
    scroll_top = 0
    while True:

        stdscr.clear()

        # Display instructions
        stdscr.addstr(0, 0, "Use arrow keys to navigate, Space to select, and Enter to submit")
    
        # Calculate the visible items based on the scroll position
        visible_items = services[scroll_top:scroll_top + height - 3]
        
        # Display checklist items
        for i, item in enumerate(visible_items):
            x = 2
            y = i + 2
            if i == current_row - 2:
                # Highlight the current item
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item)
            # Display checkmark for selected items
            if selected[i + scroll_top]:
                stdscr.addstr(y, width - 10, "[✓]")
            else:
                stdscr.addstr(y, width - 10, "[ ]")
        
        # Refresh the screen to show the changes
        stdscr.refresh()
        
        # Handle user input
        key = stdscr.getch()
        if key == curses.KEY_DOWN:
            if current_row < len(visible_items) + 1:
                current_row += 1
            else:
                if scroll_top < len(services) - height + 3:
                    scroll_top += 1
        elif key == curses.KEY_UP:
            if current_row > 2:
                current_row -= 1
            else:
                if scroll_top > 0:
                    scroll_top -= 1
        elif key == ord(" "):
            selected[current_row + scroll_top - 2] = not selected[current_row + scroll_top - 2]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            break
        
    stdscr.clear()

    return docker_compose, services, selected

def kill_docker():
    os.system("sudo kill -9 $(ps aux | grep Docker.app | awk '{print $2}' |  tr '\n' ' ') > /dev/null 2>&1")

def wait_until_start():
    while True:
            if os.system("docker ps > /dev/null 2>&1") == 0:
                break
            time.sleep(1)      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',  default='default_file', help='Pass docker-compose file as path.', type=str)
    parser.add_argument('-o', '--output',  default='dockercraft-compose.yaml', help='Pass the new docker-compose file as path.', type=str)
    subparsers = parser.add_subparsers(dest='command', required=True)
    parser_run = subparsers.add_parser('gen', help='Generate new docker compose file')
    parser_run = subparsers.add_parser('run', help='Run dockercraft-compose file')
    parser_run = subparsers.add_parser('down', help='Removes all docker compose containers and images from main docker compose. By default it will use docker-compose.yaml file.')
    parser_run = subparsers.add_parser('clean', help='It will prune all unused network, builds, containers and so on.')
    
    args = parser.parse_args()
    
    if args.command == 'gen':
        try:
            if args.file == 'default_file':
                args.file = 'docker-compose.yaml'
            
            if not os.path.exists(args.file):
                print(f"{args.file} - File not found")
                exit(1)
            docker_compose, services, selected = curses.wrapper(main, args.file)
        except KeyboardInterrupt:
            pass
        
        new_docker_compose = docker_compose.copy()
        new_docker_compose["services"] = {}
        for i in range(len(services)):
            if selected[i]:
                new_docker_compose["services"][services[i]] = docker_compose["services"][services[i]]
        
        # convert new_docker_compose to yaml and write to file
        with open(args.output, 'w') as file:
            yaml.dump(new_docker_compose, file)
        

        
        print(f"[+] New docker-compose file generated at {args.output}")
        print(f"[+] Don't delete old docker compose file {args.file}. It will be used to remove the containers and images.") 
    if args.command == 'run':
        # Restart docker in mac machine
        if args.file == 'default_file':
            args.file = 'dockercraft-compose.yaml'

        kill_docker()

        while True:
            if os.system("open -a Docker > /dev/null 2>&1") == 0:
                break

        wait_until_start()

        import subprocess
        try:
            subprocess.run(['docker-compose', '-f', args.file, 'up'])
        except KeyboardInterrupt:
            subprocess.run(['docker-compose', '-f', args.file, 'down'])
    
    if args.command == 'down':
        if args.file == 'default_file':
            args.file = 'docker-compose.yaml'
        import subprocess
        try:
            subprocess.run(['docker-compose', '-f', args.file, 'down'])
        except KeyboardInterrupt:
            pass
        kill_docker()
        wait_until_start
        print("[+] All containers and images removed.")

    if args.command == 'clean':
        import subprocess
        try:
            subprocess.run(['docker', 'system', 'prune'])
        except KeyboardInterrupt:
            pass
        print("[+] All unused network, builds, containers, and build cache are removed.")
