import subprocess
import sys
import os

def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def main():
    if len(sys.argv) < 2:
        print("""
🚗 Car Manual RAG - Management Tool

Usage: python manage.py <command>

Commands:
  start          Start all containers
  stop           Stop all containers
  restart        Restart all containers
  status         Show container status
  logs           Show logs (use Ctrl+C to exit)
  process        Process car manual
  demo           Run interactive demo
  db-shell       Access database shell
  clean          Remove all containers and data
  rebuild        Rebuild containers from scratch
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        print("🚀 Starting Car Manual RAG system...")
        run_command("docker-compose up -d")
        print("✅ System started!")
        
    elif command == "stop":
        print("🛑 Stopping system...")
        run_command("docker-compose down")
        print("✅ System stopped!")
        
    elif command == "restart":
        print("🔄 Restarting system...")
        run_command("docker-compose restart")
        print("✅ System restarted!")
        
    elif command == "status":
        print("📊 Container Status:\n")
        run_command("docker-compose ps")
        
    elif command == "logs":
        print("📜 Showing logs (Ctrl+C to exit)...\n")
        os.system("docker-compose logs -f")
        
    elif command == "process":
        print("📄 Processing car manual...\n")
        os.system("docker-compose exec rag_app python scripts/process_document.py")
        
    elif command == "demo":
        print("💬 Starting interactive demo...\n")
        os.system("docker-compose exec rag_app python demo_rag.py")
        
    elif command == "db-shell":
        print("🗄️ Accessing database shell...\n")
        os.system("docker-compose exec postgres psql -U rag_user -d car_manual_db")
        
    elif command == "clean":
        response = input("⚠️ This will remove all data. Continue? (y/N): ")
        if response.lower() == 'y':
            print("🧹 Cleaning up...")
            run_command("docker-compose down -v")
            print("✅ All data removed!")
        else:
            print("❌ Cancelled")
            
    elif command == "rebuild":
        print("🔨 Rebuilding containers...")
        run_command("docker-compose build --no-cache")
        run_command("docker-compose up -d")
        print("✅ Rebuild complete!")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python manage.py' to see available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()