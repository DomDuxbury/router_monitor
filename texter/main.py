from kafka import KafkaConsumer


def main():
    consumer = KafkaConsumer(
        "text_notifications",
        bootstrap_servers="localhost:9092",
    )

    for message in consumer:
        print(message.value.decode("utf-8"))


if __name__ == "__main__":
    main()
