import asyncio


async def main():
    '''
	source, err := v.Resources("source_name")
	if err != nil {
		return err
	}

	rr, err := source.Records("collection_name", nil)
	if err != nil {
		return err
	}

	res, _ := v.Process(rr, Anonymize{})

	dest, err := v.Resources("dest_name")
	if err != nil {
		return err
	}

	err = dest.Write(res, "collection_name", nil)
	if err != nil {
		return err
	}

	return nil
	}
type Anonymize struct{}

func (f Anonymize) Process(rr []turbine.Record) ([]turbine.Record, []turbine.RecordWithError) {
	return rr, nil
}
    '''
    pass

asyncio.run(main())
