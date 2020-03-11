import csv

def load_csv(filename):

    with open('dataset_valid.csv', mode='w') as csvfile:
        fieldnames = ['channel_id','id','date', 'message', 'url', 'site_name', 'title', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(filename, 'r') as csv_file:
            reader = csv.DictReader(csv_file)

            i = 0
            ch1 = True
            ch2 = True
            ch3 = True
            ch4 = True

            for row in reader:
                # 1018448328 1222728626 1109035330 1303657131
                if row["channel_id"] == "1018448328" and ch1 is True:
                    if i == 3050:
                        ch1 = False
                        i = 0
                    else:
                        writer.writerow(row)

                elif row["channel_id"] == "1222728626" and ch2 is True:
                    if i == 3200:
                        ch2 = False
                        i = 0
                    else:
                        writer.writerow(row)

                elif row["channel_id"] == "1109035330" and ch3 is True:
                    if i == 3200:
                        ch3 = False
                        i = 0
                    else:
                        writer.writerow(row)

                elif row["channel_id"] == "1303657131" and ch4 is True:
                    if i == 3200:
                        ch4 = False
                        i = 0
                        # break
                    else:
                        writer.writerow(row)
                i += 1



if __name__ == '__main__':
    load_csv("dataset.csv")