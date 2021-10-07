from index import download_submission_by_cid, FailToCatchContestError


def main():
    while True:
        try:
            download_submission_by_cid(int(input('輸入contest id: ')))
        except (ValueError, TypeError):
            print('請輸入數字')
        except FailToCatchContestError as e:
            print(e)
            continue
        except EOFError:
            break


if __name__ == '__main__':
    main()
