import Collector

def main():
    col = Collector.collector()
    try:
        col.getByCity("san franscisco", "california")
    finally:
        col.quit()

main()