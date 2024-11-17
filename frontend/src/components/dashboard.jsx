import { useState, useEffect, useContext } from 'react';
import { Box, Select, Button, DataTable, Heading, Text, Spinner, ResponsiveContext } from 'grommet';
import HoldingsJson from './holdings.json'

const PercentageDisplay = ({ corpus_per }) => {
    const formattedValue = corpus_per === null ? '-' : parseFloat(corpus_per).toFixed(2) + '%';
    return formattedValue;
};

const columns = [
    { property: 'company_name', header: 'Name' },
    { property: 'sector_name', header: 'Sector' },
    { property: 'instrument_name', header: 'Instrument' },
    {
        property: 'corpus_per',
        header: 'Assets',
        render: x => PercentageDisplay(x)
    }
];

const common_holdings_columns = [
    { property: 'company_name', header: 'Name' },
    { property: 'sector_name', header: 'Sector' },
    { property: 'instrument_name', header: 'Instrument' },
    {
        property: 'corpus_mf1',
        header: 'Assets in MF1',
        render: x => PercentageDisplay({ corpus_per: x['corpus_mf1'] })
    },
    {
        property: 'corpus_mf2',
        header: 'Assets in MF2',
        render: x => PercentageDisplay({ corpus_per: x['corpus_mf2'] })
    }
];

const BASE_URL = 'https://bnpxgt13ci.execute-api.us-east-1.amazonaws.com'
// const BASE_URL = 'http://127.0.0.1:8000'

const Dashboard = () => {
    const [options1, setOptions1] = useState([]);
    const [originalOptions1, setOriginalOptions1] = useState([]);
    const [value1, setValue1] = useState({});

    const [options2, setOptions2] = useState([]);
    const [originalOptions2, setOriginalOptions2] = useState([]);
    const [value2, setValue2] = useState({});

    const [mf1Info, setMf1Info] = useState({});
    const [mf2Info, setMf2Info] = useState({});
    const [commonHoldings, setCommonHoldings] = useState([]);

    const [isLoading, setIsLoading] = useState(false);
    const [overlapPercentage, setOverlapPercentage] = useState();

    useEffect(() => {
        // fetch(BASE_URL+'/mutualfunds')
        //     .then(response => response.json())
        //     .then(data => {
                // setOptions1(data);
                // setOriginalOptions1(data);
                // setOptions2(data);
                // setOriginalOptions2(data);
        //     })
        //     .catch(error => console.error('Error fetching data:', error));
        setOptions1(HoldingsJson);
        setOriginalOptions1(HoldingsJson);
        setOptions2(HoldingsJson);
        setOriginalOptions2(HoldingsJson);
    }, []);


    const onCompareMutualFundClick = () => {
        setIsLoading(true);
        if (value1 && value2 && value1.mutual_fund_id && value2.mutual_fund_id) {
            setMf1Info({});
            setMf2Info({});
            setCommonHoldings([]);

            fetch(BASE_URL+'/compare-mutual-funds', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mutual_fund1: value1.mutual_fund_id, mutual_fund2: value2.mutual_fund_id }),
            })
                .then(response => response.json())
                .then(data => {
                    if (value1.mutual_fund_id in data) {
                        setMf1Info(data[value1.mutual_fund_id]);
                    }
                    if (value2.mutual_fund_id in data) {
                        setMf2Info(data[value2.mutual_fund_id]);
                    }
                    if ('intersection_holdings' in data) {
                        setCommonHoldings(data['intersection_holdings']);
                    }
                    setOverlapPercentage(data['overlap_percentage']);
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    setIsLoading(false);
                });
        }
    };

    const size = useContext(ResponsiveContext);

    const adjustedColumns = size === 'small'
    ? columns.filter(col => col.property !== 'sector_name' && col.property !== 'instrument_name')
    : columns;
    
    const adjustedHoldingsColumns = size === 'small'
    ? common_holdings_columns.filter(col => col.property !== 'sector_name' && col.property !== 'instrument_name')
    : common_holdings_columns;

    return (
        <>
            <Box align="center" justify="start" pad={{ top: '12%' }}>
                {options1.length === 0 &&
                    <>
                        <Spinner size='medium' color='brand' />
                        <Text margin={{ "top": "small" }} color='brand'>Loading mutual funds</Text>
                    </>}
                {options1.length > 0 && (
                    <Box direction={size === 'small' ? 'column' : 'row'} gap="medium">
                        <Box pad="large" background="light-2" round>
                            <Text margin={{ "bottom": "small" }}>Mutual Fund 1</Text>
                            <Select
                                size="medium"
                                placeholder="Select mutual fund"
                                labelKey="fund_name"
                                value={value1.fund_name}
                                options={options1}
                                onChange={({ option }) => setValue1(option)}
                                onClose={() => setOptions1(originalOptions1)}
                                onSearch={(text) => {
                                    const escapedText = text.replace(/[-\\^$*+?.()|[\]{}]/g, '\\$&');
                                    const exp = new RegExp(escapedText, 'i');
                                    setOptions1(originalOptions1.filter((o) => exp.test(o.fund_name)));
                                }}
                            />
                        </Box>

                        <Box pad="large" background="light-2" round>
                            <Text margin={{ "bottom": "small" }}>Mutual Fund 2</Text>
                            <Select
                                size="medium"
                                placeholder="Select mutual fund"
                                labelKey="fund_name"
                                value={value2.fund_name}
                                options={options2}
                                onChange={({ option }) => setValue2(option)}
                                onClose={() => setOptions2(originalOptions2)}
                                onSearch={(text) => {
                                    const escapedText = text.replace(/[-\\^$*+?.()|[\]{}]/g, '\\$&');
                                    const exp = new RegExp(escapedText, 'i');
                                    setOptions2(originalOptions2.filter((o) => exp.test(o.fund_name)));
                                }}
                            />
                        </Box>
                    </Box>
                )}

                {options1.length > 0 && (
                    <Box pad="large">
                        <Button
                            primary
                            label="Calculate Holdings Overlap"
                            onClick={onCompareMutualFundClick}
                            disabled={!value1.mutual_fund_id || !value2.mutual_fund_id}
                            style={{
                                backgroundColor: '#DB7093',
                                color: 'white',
                                border: 'none',
                                padding: '10px 20px',
                                borderRadius: '5px',
                                cursor: 'pointer',
                                fontSize: '16px'
                            }}
                        />
                    </Box>
                )}
            </Box>

            {isLoading && <Box align="center"><Spinner size="medium" color="brand" /></Box>}

            <Box direction={size === 'small' ? 'column' : 'row'} gap="medium">
                {mf1Info.hasOwnProperty('holdings') && mf1Info.holdings.length > 0 && (
                    <Box align="center" pad="large">
                        <Box direction="row" align="center" gap="small">
                            <img src={mf1Info.logo_url} alt={mf1Info.fund_name} style={{ width: '54px', height: '54px' }} />
                            <Heading level={2} margin="small">{mf1Info.fund_name}</Heading>
                        </Box>

                        <Heading level={5} margin="small">Total Holdings {mf1Info.holdings.length}</Heading>
                        <DataTable
                            columns={adjustedColumns.map((c) => ({
                                ...c,
                                // search: c.property === 'company_name' || c.property === 'instrument_name',
                            }))}
                            data={mf1Info.holdings.map((holding, index) => ({ ...holding, key: index }))}
                        // sort={sort}
                        // onSort={setSort}
                        // resizeable
                        />
                    </Box>
                )}

                {mf2Info.hasOwnProperty('holdings') && mf2Info.holdings.length > 0 && (
                    <Box align="center" pad="large">
                        <Box direction="row" align="center" gap="small">
                            <img src={mf2Info.logo_url} alt={mf2Info.fund_name} style={{ width: '54px', height: '54px' }} />
                            <Heading level={2} margin="small">{mf2Info.fund_name}</Heading>
                        </Box>
                        <Heading level={5} margin="small">Total Holdings {mf2Info.holdings.length}</Heading>
                        <DataTable
                            columns={adjustedColumns.map((c) => ({
                                ...c,
                                // search: c.property === 'company_name' || c.property === 'instrument_name',
                            }))}
                            data={mf2Info.holdings.map((holding, index) => ({ ...holding, key: index }))}
                        // sort={sort}
                        // onSort={setSort}
                        // resizeable
                        />
                    </Box>
                )}
            </Box>

            {commonHoldings.length > 0 && (
                <Box align="center" pad="large">
                    <Heading level={2} margin="small">Intersection or Common Holdings</Heading>
                    <Heading level={5} margin="small">Total Holdings {commonHoldings.length}</Heading>
                    {overlapPercentage && (
                        <Heading level={4} margin="small">Overlap Percentage {overlapPercentage}</Heading>
                    )}
                    <DataTable
                        columns={adjustedHoldingsColumns.map((c) => ({
                            ...c,
                            // search: c.property === 'company_name' || c.property === 'instrument_name',
                        }))}
                        data={commonHoldings.map((holding, index) => ({ ...holding, key: index }))}
                    // sort={sort}
                    // onSort={setSort}
                    // resizeable
                    />
                </Box>
            )}
        </>
    );
};

export default Dashboard;